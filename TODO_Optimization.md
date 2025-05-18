# Performance Optimization TODO List

This document outlines simple performance improvements for our Park Security Flask app, with potential drawbacks explained.

## 1. Optimize Database Queries

**What it means:** Get multiple pieces of information in one request instead of many separate requests.

**How it helps:** Fewer trips to the database means faster responses.

**Simple implementation:**
```python
# Instead of two separate queries:
# yes_count_res = supabase.table('votes').select('id', count='exact').eq('scenario_id', scenario_id).eq('decision', True).execute()
# no_count_res = supabase.table('votes').select('id', count='exact').eq('scenario_id', scenario_id).eq('decision', False).execute()

# Use a single query with aggregation:
counts = supabase.from_('votes')
    .select('decision, count')
    .eq('scenario_id', scenario_id)
    .group_by('decision')
    .execute()
```

**Drawbacks:**
- Slightly more complex code
- Might require specific database features that not all providers support

**Need to check:**
- If supabase would allow such operation.

## 2. Session Optimization

**What it means:** Store less data in user sessions and don't update them unnecessarily.

**How it helps:** Reduces the amount of data transferred with each request.

**Simple implementation:**
```python
# Only mark session as modified when truly needed
# Instead of doing this repeatedly:
session.modified = True

# Do this only when you've actually changed something important
if something_actually_changed:
    session.modified = True
```

**Drawbacks:**
- Need to be careful not to break session tracking
- Might miss saving some user data if implemented incorrectly

**Need to check:**
- What exactly is currently being transferred with each request and what would change.

## 3. Frontend Optimizations

**What it means:** Load styles and scripts faster and more efficiently.

**How it helps:** Pages load quicker for users.

**Simple implementation:**
- Self-host Tailwind instead of using CDN
- Add file hashes to prevent browser caching issues

**Drawbacks:**
- Self-hosting requires setting up build processes
- More complex deployment process
- Might need additional tools/dependencies

**Need to check:**
- How this would impact fly.io deployment.

## 4. Remove Debug Logging

**What it means:** Stop writing detailed debug messages in the production version.

**How it helps:** Less processing time spent writing logs.

**Simple implementation:**
```python
# Instead of:
app.logger.debug(f"[DEBUG] vote_data: {vote_data}")

# Use:
if app.debug:
    app.logger.debug(f"[DEBUG] vote_data: {vote_data}")
```

**Drawbacks:**
- Harder to troubleshoot issues in production 
- Might miss important diagnostic information

## 5. Reduce API Response Size

**What it means:** Send only the data that's actually needed.

**How it helps:** Smaller responses load faster.

**Simple implementation:**
```python
# Instead of sending everything:
return jsonify({
    'scenario': next_scenario,
    'progress': progress,
    'current_scenario_number': current_index + 1,
    'total_scenarios': TOTAL_SCENARIOS,
    'emoji': emoji  # Can be removed if calculated client-side
})
```

**Drawbacks:**
- Might need to calculate some values on the client-side
- Could make the JavaScript slightly more complex

**Need to check:**
- What exactly are the drawbacks on making simple calculations on the client-side
- How much more complex de JavaScript would need to be

## 6. Consider Async Operations

**What it means:** Let the app do other things while waiting for database operations.

**How it helps:** Can handle more users at once.

**Simple implementation:**
- Would require switching to an async framework like FastAPI
- More complex code changes

**Drawbacks:**
- Major code rewrite required
- More complex programming model
- Might introduce new bugs during conversion


# Will not be added

## 1. Add Caching

**What it means:** Store information we use often so we don't need to keep calculating it each time.

**How it helps:** Makes the app faster by reducing work.

**Simple implementation:**
```python
# Add to the top of app.py
from functools import lru_cache

# Then wrap functions that calculate the same thing repeatedly
@lru_cache(maxsize=128)
def get_vote_counts(scenario_id):
    # Your existing vote counting code here
    return yes_votes, no_votes
```

**Drawbacks:**
- Might show slightly outdated information if many people vote at once
- Uses more memory (RAM) on your server
- Requires careful planning to know when to clear the cache

**Reason why this will not be added:**
- I'm not interested in having to deal with cache clearing.
- Using more memory might make hosting this application more expensive.

## 2. HTTP Optimizations

**What it means:** Use web server tricks to send files faster.

**How it helps:** Reduces download time for users.

**Simple implementation:**
- Add proper cache headers for static files
- Enable compression in your web server

**Drawbacks:**
- May require web server configuration (Nginx/Apache)
- Caching requires careful handling of version updates

**Reason why this will not be added:**
- Don't want to add more complexity (Nginx/Apache) to this project
- Caching seems to add unnecessary complexity