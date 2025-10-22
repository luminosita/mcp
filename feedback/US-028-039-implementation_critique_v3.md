Create a new git branch for the refactoring

## File Caching and Loading Staretegy

We unifed cache service implemented, we also have unifed FileLoader implemented. We are missing unified loading file from cache, and if not existing from disk using FileLoader

New class, CacheFileLoader should validate filename and filepaths using FileValidator per resource type (templates, prompt, sdlc, artifact). It should handle complete logic of looking up a cache, and if it's a miss, loading it from FileLoader.

Each resource method must be tiny. It is allowed only to call CacheFileLoader and pass loaded file to the response. It should not be concerned with loading from disk and cache operations.

FileValidator can be implemented or common one can be initialized at the very beginning and instance of it passed to CacheFileLoader by method to get a resource.

Completely remove PromptGeneratorScanner and PromptRegistry. Prompt retrieval must use the same logic as the rest of the resources (CacheFileLoader)
