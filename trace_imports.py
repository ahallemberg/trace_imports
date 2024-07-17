import sys
import os
import builtins

def trace_imports(main_script, script_args, filter_path=None):
    imported_modules = set()
    original_import = builtins.__import__

    def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
        module = original_import(name, globals, locals, fromlist, level)
        if hasattr(module, '__file__'):
            file_path = os.path.abspath(module.__file__)
            if filter_path is None or file_path.startswith(filter_path):
                imported_modules.add(file_path)
        return module

    builtins.__import__ = custom_import

    original_argv = sys.argv
    sys.argv = [main_script] + script_args

    try:
        with open(main_script, 'r') as file:
            exec(file.read(), {'__name__': '__main__'})
    except Exception as e:
        print(f"An error occurred while executing the script: {e}")
    finally:
        builtins.__import__ = original_import
        sys.argv = original_argv

    return imported_modules

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trace_imports.py <path_to_your_main_script> [--filter-path <path>] [script arguments...]")
        sys.exit(1)

    main_script = sys.argv[1]
    script_args = []
    filter_path = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--filter-path':
            if i + 1 < len(sys.argv):
                filter_path = os.path.abspath(sys.argv[i + 1])
                i += 2
            else:
                print("Error: --filter-path requires a path argument")
                sys.exit(1)
        else:
            script_args.append(sys.argv[i])
            i += 1

    imported_files = trace_imports(main_script, script_args, filter_path)

    print("\nImported files:")
    for file in sorted(imported_files):
        print(file)
