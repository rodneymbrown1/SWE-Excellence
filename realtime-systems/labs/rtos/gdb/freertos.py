"""freertos.py -- teach gdb about FreeRTOS tasks.  A few commands, written against kernel V11.x single-core data structures.

    source labs/rtos/gdb/freertos.py

    fr-tasks          every task: state, priority (and base priority if it was boosted by inheritance), what it waits on
    fr-tick           the kernel tick count and the running task
    fr-queue EXPR     a queue/semaphore/mutex: items waiting, mutex holder, tasks blocked on it

Why this exists: gdb's thread list shows one CPU; an RTOS multiplexes many tasks on it.  The kernel's own lists are the
truth, and gdb can read them.  The same technique works for any framework's task/queue tables (see the Debugging project).
Requires an unoptimised build (make OPT=-O0) so that the kernel's static variables are visible.
"""
import gdb


def _val(expr):
    return gdb.parse_and_eval(expr)


def _list_items(lst):
    """Yield the owner (TCB pointer) of every item in a FreeRTOS List_t value."""
    n = int(lst["uxNumberOfItems"])
    end = lst["xListEnd"].address
    item = end["pxNext"]
    count = 0
    while int(item) != int(end.cast(item.type)) and count < n + 1:
        yield item["pvOwner"]
        item = item["pxNext"]
        count += 1


def _tcb(owner):
    return owner.cast(gdb.lookup_type("tskTCB").pointer())


def _name(tcb):
    return tcb["pcTaskName"].string()


def _current_tcb():
    for sym in ("pxCurrentTCB", "pxCurrentTCBs[0]"):
        try:
            return _val(sym)
        except gdb.error:
            continue
    return None


def _queue_of_event_list(container):
    """container points at a Queue_t's xTasksWaitingToReceive / ToSend list; recover the Queue_t address."""
    qt = gdb.lookup_type("Queue_t")
    addr = int(container)
    for field in ("xTasksWaitingToReceive", "xTasksWaitingToSend"):
        off = int(gdb.parse_and_eval("(unsigned long)&((Queue_t *)0)->%s" % field))
        q = addr - off
        # accept only if the queue's own list address matches
        try:
            qp = gdb.Value(q).cast(qt.pointer())
            if int(qp[field].address) == addr:
                return q, ("receive" if field == "xTasksWaitingToReceive" else "send")
        except gdb.error:
            pass
    return None, None


class FrTasks(gdb.Command):
    """List all FreeRTOS tasks with state and priority."""

    def __init__(self):
        super().__init__("fr-tasks", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        cur = _current_tcb()
        groups = []
        nprio = int(gdb.parse_and_eval("sizeof(pxReadyTasksLists)/sizeof(pxReadyTasksLists[0])"))
        for p in range(nprio):
            groups.append(("ready", _val("pxReadyTasksLists[%d]" % p)))
        groups.append(("delayed", _val("*pxDelayedTaskList")))
        groups.append(("delayed(overflow)", _val("*pxOverflowDelayedTaskList")))
        groups.append(("suspended/blocked-forever", _val("xSuspendedTaskList")))
        groups.append(("pending-ready", _val("xPendingReadyList")))
        rows = []
        for state, lst in groups:
            for owner in _list_items(lst):
                t = _tcb(owner)
                prio, base = int(t["uxPriority"]), int(t["uxBasePriority"])
                running = cur is not None and int(owner) == int(cur)
                waits = ""
                cont = t["xEventListItem"]["pvContainer"]
                if int(cont) != 0:
                    q, kind = _queue_of_event_list(cont)
                    waits = "blocked on queue/semaphore @0x%x (waiting to %s)" % (q, kind) if q else "blocked on event list"
                st = "RUNNING" if running else state
                boosted = "" if prio == base else "  <-- priority %d inherited (base %d)" % (prio, base)
                rows.append((-prio, _name(t), st, prio, waits + boosted))
        rows.sort()
        print("%-12s %-26s %4s  %s" % ("task", "state", "prio", "notes"))
        for _, name, st, prio, notes in rows:
            print("%-12s %-26s %4d  %s" % (name, st, prio, notes))


class FrTick(gdb.Command):
    """Show tick count and current task."""

    def __init__(self):
        super().__init__("fr-tick", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        cur = _current_tcb()
        print("tick = %d   running = %s" % (int(_val("xTickCount")), _name(_tcb(cur)) if cur is not None and int(cur) else "(none)"))


class FrQueue(gdb.Command):
    """fr-queue EXPR : describe a queue / semaphore / mutex handle."""

    def __init__(self):
        super().__init__("fr-queue", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        q = gdb.parse_and_eval(arg).cast(gdb.lookup_type("Queue_t").pointer())
        print("items waiting = %d   length = %d   item size = %d" % (int(q["uxMessagesWaiting"]), int(q["uxLength"]), int(q["uxItemSize"])))
        try:
            holder = q["u"]["xSemaphore"]["xMutexHolder"]
            if int(q["uxItemSize"]) == 0 and int(q["pcHead"]) == 0:      # mutex-type: pcHead is NULL
                print("mutex holder = %s" % (_name(_tcb(holder)) if int(holder) else "(nobody)"))
            else:
                print("(no owner: counting/binary semaphores and queues are not owned by anyone)")
        except gdb.error:
            pass
        for kind in ("xTasksWaitingToReceive", "xTasksWaitingToSend"):
            names = [_name(_tcb(o)) for o in _list_items(q[kind])]
            if names:
                print("%s: %s" % (kind, ", ".join(names)))


FrTasks()
FrTick()
FrQueue()
print("freertos.py loaded: fr-tasks, fr-tick, fr-queue")
