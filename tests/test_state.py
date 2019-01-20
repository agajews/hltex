# from hltex.state import State

# def test_run():
#     source = "Hello"
#     state = State(source)

#     def f(state):
#         state.pos += 2
#         return "hey"

#     res = state.run(f)
#     assert res == "hey"
#     assert state.pos == 2


# def test_run_kwargs():
#     source = "Hello"
#     state = State(source)

#     def f(state, a=0, b=2):
#         state.pos += 2
#         assert a == 3 and b == 1
#         return "hey"

#     res = state.run(f, a=3, b=1)
#     assert res == "hey"
#     assert state.pos == 2


# def test_run_none():
#     source = "Hello"
#     state = State(source)

#     def f(state, a=0, b=2):
#         state.pos += 2
#         assert a == 3 and b == 1
#         return None

#     res = state.run(f, a=3, b=1)
#     assert res is None
#     assert state.pos == 0


# def test_run_nested():
#     source = "Hello"
#     state = State(source)

#     def g(state, a=1, b=3):
#         state.pos += 1
#         assert a == 5, b == 6
#         return "o"

#     def f(state, a=0, b=2):
#         state.pos += 2
#         assert a == 3 and b == 1
#         return "hey", g, {"a": 5, "b": 6}

#     res = state.run(f, a=3, b=1)
#     assert res == "heyo"
#     assert state.pos == 3


# def test_run_nested_none():
#     source = "Hello"
#     state = State(source)

#     def g(state, a=1, b=3):
#         state.pos += 1
#         assert a == 5, b == 6
#         return "o", None

#     def f(state, a=0, b=2):
#         state.pos += 2
#         assert a == 3 and b == 1
#         return "hey", g, {"a": 5, "b": 6}

#     res = state.run(f, a=3, b=1)
#     assert res == "heyo"
#     assert state.pos == 3
