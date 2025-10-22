## Caching Staretegy

**Issues:**
- PromptCache is in-memory implementation. Does not belong in prompts folder and name should not be PromptCache if it is representing general in-mem cache implementation
**Solution:**
- Rename and move

**Rationale**
Prompts, templates, patterns and artifacts are essentially files on the disk and must be treated the same way

## Duplications

### File: src/mcp_server/services/cache.py

**Issues**
- _get_or_fetch_redis and _get_or_fetch_memory are nearly identical. Only cache repository is different (Redis vs in-memory)

**Solution**
- unify methods are remove duplication

### File: src/mcp_server/services/cache.py

**Issues**
- _get_or_fetch_redis and _get_or_fetch_memory are nearly identical. Only cache repository is different (Redis vs in-memory)

**Solution**
- unify methods are remove duplication

### File: src/mcp_server/api/routes/resources.py

**Issues**
- get_pattern_resource, get_sdlc_core_resource, get_template_resource are nearly identical and duplication of logic
- load_resource_file, used exclusevely for testing, is duplication of logic in load_resource_file_cached and in _load_file_from_disk

**Solution**
Remove duplications. Bad for maintenance

### File: src/mcp_server/prompts/registry.py

**Issues**

- load_prompt and _load_file_from_disk methods are using the same logic for loading files as templates, patterns, artifacts

**Solution**
- Unify all file loading methods in one utility class
