# Practice target for the State First book.
# -O0 -g : no optimisation, full debug info, so nothing is "<optimized out>".
CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O0 -g -Wall -Wextra

gateway: gateway.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

run: gateway
	./gateway --max 400

clean:
	rm -rf gateway gateway.dSYM

.PHONY: run clean
