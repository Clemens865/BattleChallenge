# Task: File Organizer

## Requirements

Create a Python module `file_organizer.py` that exports a function `organize_files(source_dir: str, target_dir: str) -> dict`.

The function moves files from `source_dir` into subdirectories of `target_dir` organized by file extension.

### Behavior

1. Scan all files in `source_dir` (non-recursive, top-level only)
2. For each file, determine its extension (lowercase, without the dot)
   - Files with no extension go into a folder named `other`
3. Create subdirectories in `target_dir` named after extensions (e.g., `txt`, `pdf`, `jpg`)
4. Move each file into the appropriate subdirectory
5. Return a dictionary mapping extension names to lists of filenames moved
   - e.g., `{"txt": ["notes.txt", "readme.txt"], "pdf": ["doc.pdf"]}`
6. Skip directories (do not move subdirectories)
7. If a file with the same name already exists in the target, rename by appending `_1`, `_2`, etc. before the extension
   - e.g., `notes.txt` becomes `notes_1.txt`

### Constraints

- No external dependencies (stdlib only)
- Must not delete the source directory
- Must create target subdirectories as needed

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- Files are physically moved (not copied)
- Original files no longer exist in source_dir after organization
