// gateway.cpp -- practice target for the "State First" method.
//
// A tiny event-driven link monitor. It is shaped like real embedded/server code:
//   * one endless loop pulling events from a stream (Tick, Heartbeat, Data)
//   * one class (LinkMonitor) that owns the state you care about
//   * a few rarely-taken paths
//
// Build:   make                  (-O0 -g so every variable is visible in the debugger)
// Run:     ./gateway --max 400   (omit --max to run forever, like the real thing; Ctrl-C to stop)
//
// REQUIREMENT (what the product owner wrote):
//   R1. Down -> Up        after 3 consecutive heartbeats.
//   R2. Up -> Degraded    when 4 ticks pass with no heartbeat.
//   R3. Degraded -> Down  when 8 ticks pass with no heartbeat.
//   R4. Degraded -> Up    after 2 consecutive heartbeats.
//   R5. A link that is receiving heartbeats must not be declared Down.
//   R6. Data is forwarded only while the link is Up; otherwise it is dropped.

#include <cstdio>
#include <cstdlib>
#include <cstring>

enum class EventType { Tick, Heartbeat, Data };
enum class LinkState { Down, Up, Degraded };

static const char* name(LinkState s) {
  switch (s) {
    case LinkState::Down:     return "Down";
    case LinkState::Up:       return "Up";
    case LinkState::Degraded: return "Degraded";
  }
  return "?";
}

struct Event {
  EventType type;
  int tick;
  int payload;
};

// A deterministic fake world: heartbeats stop during "outage" windows.
class EventSource {
 public:
  Event next() {
    for (;;) {
      switch (phase_) {
        case 0:
          phase_ = 1;
          return Event{EventType::Tick, tick_, 0};
        case 1:
          phase_ = 2;
          if (!in_outage(tick_)) return Event{EventType::Heartbeat, tick_, 0};
          break;
        default: {
          phase_ = 0;
          int t = tick_++;
          if (t % 3 == 0) return Event{EventType::Data, t, t + 9};
          break;
        }
      }
    }
  }

 private:
  static bool in_outage(int t) {
    return (t >= 20 && t < 26) || (t >= 60 && t < 62) || (t >= 120 && t < 132);
  }
  int tick_ = 1;
  int phase_ = 0;
};

class LinkMonitor {
 public:
  void on_event(const Event& e) {
    now_ = e.tick;
    switch (e.type) {
      case EventType::Tick:      on_tick();      break;
      case EventType::Heartbeat: on_heartbeat(); break;
      case EventType::Data:      ++data_seen_;   break;
    }
  }

  LinkState state() const { return state_; }
  int data_seen() const { return data_seen_; }

 private:
  static constexpr int kDegradeAfter = 4;  // R2
  static constexpr int kDownAfter = 8;     // R3
  static constexpr int kUpAfter = 3;       // R1
  static constexpr int kRecoverAfter = 2;  // R4

  void on_tick() {
    ++missed_;
    if (state_ == LinkState::Up && missed_ >= kDegradeAfter) {
      LinkState from = state_;
      state_ = LinkState::Degraded;
      good_ = 0;
      announce(from);
    } else if (state_ == LinkState::Degraded && missed_ >= kDownAfter) {
      LinkState from = state_;
      state_ = LinkState::Down;
      good_ = 0;
      announce(from);
    }
  }

  void on_heartbeat() {
    if (state_ == LinkState::Up) {
      missed_ = 0;
    } else if (state_ == LinkState::Down) {
      missed_ = 0;
      if (++good_ >= kUpAfter) {
        LinkState from = state_;
        state_ = LinkState::Up;
        announce(from);
      }
    } else {  // Degraded
      if (++good_ >= kRecoverAfter) {
        LinkState from = state_;
        state_ = LinkState::Up;
        missed_ = 0;
        announce(from);
      }
    }
  }

  void announce(LinkState from) const {
    std::printf("[t=%3d] %-8s -> %-8s (missed=%d good=%d)\n", now_, name(from),
                name(state_), missed_, good_);
  }

  LinkState state_ = LinkState::Down;
  int missed_ = 0;     // ticks since the last heartbeat
  int good_ = 0;       // consecutive heartbeats seen
  int now_ = 0;
  int data_seen_ = 0;
};

class Gateway {
 public:
  explicit Gateway(int max_events) : max_(max_events) {}

  void run() {
    int n = 0;
    while (max_ < 0 || n < max_) {  // max_ < 0 means "forever"
      Event e = source_.next();
      dispatch(e);
      ++n;
    }
  }

  void summary() const {
    std::printf("final: state=%s forwarded=%d dropped=%d data_seen=%d\n",
                name(monitor_.state()), forwarded_, dropped_, monitor_.data_seen());
  }

 private:
  void dispatch(const Event& e) {
    monitor_.on_event(e);
    if (e.type == EventType::Data) {
      if (monitor_.state() == LinkState::Up) ++forwarded_;  // R6
      else ++dropped_;
      if (e.payload >= 99) flush_burst(e);  // rare path: big payloads trigger a burst
    }
  }

  void flush_burst(const Event& e) {
    for (int i = 0; i < 3; ++i) {
      Event extra{EventType::Data, e.tick, e.payload + i};
      monitor_.on_event(extra);
    }
  }

  int max_;
  EventSource source_;
  LinkMonitor monitor_;
  int forwarded_ = 0;
  int dropped_ = 0;
};

int main(int argc, char** argv) {
  int max_events = -1;
  for (int i = 1; i + 1 < argc; ++i)
    if (std::strcmp(argv[i], "--max") == 0) max_events = std::atoi(argv[i + 1]);
  Gateway gw(max_events);
  gw.run();
  gw.summary();
  return 0;
}
