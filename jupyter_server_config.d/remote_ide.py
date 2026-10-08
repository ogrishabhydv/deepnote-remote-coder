# Loaded by Jupyter Server in the Deepnote Python environment.
# This is deliberately additive: it does not replace Deepnote's own server
# startup command. It only enables the optional remote IDE extension.

c.ServerApp.jpserver_extensions = {
    **getattr(c.ServerApp, "jpserver_extensions", {}),
    "remote_ide_jupyter_extension": True,
}
