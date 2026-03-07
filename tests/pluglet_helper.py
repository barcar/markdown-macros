"""Minimal pluglet for tests: define_env(env) sets a variable and a macro."""

def define_env(env):
    env.variables["from_pluglet"] = "pluglet_ok"
    @env.macro
    def double(x):
        return int(x) * 2
