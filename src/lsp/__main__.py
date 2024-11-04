from lsp.app import LspApp
from lsp.handlers import registry


def main() -> int:
    app = LspApp()
    app.add_registry(registry)
    return app.run()


if __name__ == "__main__":
    main()
