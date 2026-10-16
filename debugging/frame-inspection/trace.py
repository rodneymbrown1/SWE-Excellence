# gdb: log every call as  -> func(args)  and  <- func = return value.
# Usage:  (gdb) source trace.py
#         (gdb) trace-funcs ^(add_item|compute_total|line_total|apply_discount)$
#         (gdb) run
import gdb

class Exit(gdb.FinishBreakpoint):
    def __init__(self, name):
        super().__init__(gdb.newest_frame(), internal=True)
        self.name = name
    def stop(self):
        rv = self.return_value
        print("<- %s = %s" % (self.name, rv if rv is not None else "(void)"))
        return False
    def out_of_scope(self):
        pass

class Entry(gdb.Breakpoint):
    def stop(self):
        f = gdb.selected_frame()
        args = []
        for sym in f.block():
            if sym.is_argument:
                args.append("%s=%s" % (sym.name, sym.value(f)))
        print("-> %s(%s)" % (f.name(), ", ".join(args)))
        Exit(f.name())
        return False

class TraceFuncs(gdb.Command):
    """trace-funcs REGEX : trace in/out of every function whose name matches."""
    def __init__(self):
        super().__init__("trace-funcs", gdb.COMMAND_USER)
    def invoke(self, arg, from_tty):
        import re
        rx = re.compile(arg.strip() or ".")
        for line in gdb.execute("info functions -n", to_string=True).splitlines():
            m = re.search(r"(\w+)\(", line)
            if m and rx.search(m.group(1)):
                Entry(m.group(1), internal=True)
TraceFuncs()
