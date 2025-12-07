# Error Handling Quick Reference

## For Developers: How to Add Error Handling

### Basic Pattern

```python
from app.utils.error_handling import get_error_handler

def your_method(self):
    """Your method with error handling."""
    error_handler = get_error_handler()

    try:
        # Show loading state
        self.set_activity(True)
        self.status_bar.showMessage("Doing something...")

        # Your code here
        result = risky_operation()

        # Success message
        self.status_bar.showMessage("Success!", 3000)
        self.log_debug("Operation completed", "success")

        return result

    except SpecificError as e:
        # Handle specific error
        error_handler.show_error(
            "Error Title",
            "User-friendly message explaining what went wrong.\n\n"
            "Suggestion for what to do next.",
            details=str(e),
            parent=self
        )
        self.log_debug(f"Operation failed: {e}", "error")
        return None

    finally:
        # ALWAYS clear loading state
        self.set_activity(False)
```

## Check Prerequisites

```python
def operation_requiring_geometry(self):
    """Operation that needs geometry."""
    from app.utils.error_handling import get_error_handler

    error_handler = get_error_handler()

    # Check if geometry is loaded
    if not self.has_geometry():
        error_handler.show_warning(
            "No Geometry",
            "Please load geometry from Rhino first.\n\n"
            "Use File > Load from Rhino (Ctrl+R).",
            parent=self
        )
        return

    # Proceed with operation...
```

## Show Loading State

```python
# Always use try/finally to ensure cleanup
try:
    self.set_activity(True)  # Show spinner
    self.status_bar.showMessage("Processing...")

    # Your long operation
    result = long_operation()

finally:
    self.set_activity(False)  # Hide spinner
```

## File I/O Errors

```python
try:
    with open(file_path, 'w') as f:
        json.dump(data, f)

    self.status_bar.showMessage("Saved successfully", 3000)

except PermissionError:
    error_handler.show_error(
        "Permission Denied",
        "Cannot save to this location.\n\n"
        "Try saving to a different folder.",
        parent=self
    )

except OSError as e:
    error_handler.show_error(
        "Save Error",
        f"Failed to save file:\n\n{str(e)}\n\n"
        "Check disk space and path validity.",
        details=str(e),
        parent=self
    )
```

## Using Pre-defined Messages

```python
from app.utils.error_handling import get_error_message

title, message = get_error_message('connection_refused')
error_handler.show_error(title, message, parent=self)
```

## Available Error Keys

- `connection_refused`
- `connection_timeout`
- `server_error`
- `cpp_not_available`
- `cpp_initialization_error`
- `nurbs_fitting_failed`
- `nurbs_quality_poor`
- `file_not_found`
- `file_read_error`
- `file_write_error`
- `invalid_file_format`
- `invalid_parameters`
- `constraint_violation`
- `unexpected_error`

## Dialog Types

### Error (Critical)
```python
error_handler.show_error(
    "Title",
    "Message",
    details="Technical details (optional)",
    parent=self
)
```

### Warning
```python
error_handler.show_warning(
    "Title",
    "Message",
    details="Technical details (optional)",
    parent=self
)
```

### Info
```python
error_handler.show_info(
    "Title",
    "Message",
    parent=self
)
```

### Confirmation
```python
if error_handler.confirm("Title", "Question?", parent=self):
    # User clicked Yes
    proceed()
else:
    # User clicked No
    cancel()
```

## Logging

```python
# Standard levels
self.log_debug("Message", "info")     # Blue
self.log_debug("Message", "success")  # Green
self.log_debug("Message", "warning")  # Yellow
self.log_debug("Message", "error")    # Red
self.log_debug("Message", "debug")    # Grey
```

## Error Message Guidelines

### Structure
1. **Title:** 2-3 words, specific
2. **Problem:** What went wrong
3. **Solution:** What to do next
4. **Details:** Technical info (optional, expandable)

### Good Example
```
Title: "Connection Error"
Message: "Cannot connect to Grasshopper server.

Please ensure:
1. Rhino is running
2. Grasshopper is open
3. HTTP server is active on port 8888

Try reconnecting after verifying these steps."
```

### Bad Example
```
Title: "Error"
Message: "Connection failed"
```

## Disable UI When No Data

```python
def update_ui_for_geometry_state(self):
    """Update UI based on data availability."""
    has_geom = self.has_geometry()

    # Disable/enable widgets
    self.analysis_panel.setEnabled(has_geom)

    # Set tooltips
    if not has_geom:
        self.analysis_panel.setToolTip("Load geometry from Rhino first")
```

## Using Decorators

### For Methods That Can Fail
```python
from app.utils.error_handling import handle_exceptions

@handle_exceptions(
    error_title="Analysis Error",
    user_message="Analysis failed. Try reloading geometry.",
    log_traceback=True,
    show_dialog=True,
    return_on_error=None
)
def run_analysis(self):
    # Method that might fail
    return perform_analysis()
```

### For Graceful Degradation
```python
from app.utils.error_handling import graceful_degradation

@graceful_degradation(fallback_value=[], log_error=True)
def get_regions(self):
    # May fail, returns [] on error
    return self.state.regions
```

## Common Patterns

### Network Operation
```python
try:
    self.set_activity(True)
    response = requests.get(url, timeout=2)

    if response.status_code == 200:
        self.log_debug("Connected", "success")
        return response.json()
    else:
        error_handler.show_error(
            "Server Error",
            f"Server returned status {response.status_code}",
            parent=self
        )

except Timeout:
    error_handler.show_error(
        "Connection Timeout",
        "Server did not respond in time.\n\nTry again.",
        parent=self
    )

except ConnectionError:
    title, msg = get_error_message('connection_refused')
    error_handler.show_error(title, msg, parent=self)

finally:
    self.set_activity(False)
```

### Long Operation with Progress
```python
try:
    self.set_activity(True)

    for i, item in enumerate(items):
        # Update progress
        percent = (i + 1) / len(items) * 100
        self.status_bar.showMessage(
            f"Processing {i+1}/{len(items)}..."
        )

        # Process item
        process(item)

    self.status_bar.showMessage("Complete!", 3000)

except Exception as e:
    error_handler.show_error(
        "Processing Error",
        f"Failed at item {i+1}:\n\n{str(e)}",
        details=str(e),
        parent=self
    )

finally:
    self.set_activity(False)
```

## Testing Error Handling

### Manual Testing
1. Trigger error condition
2. Verify dialog appears
3. Check message clarity
4. Verify recovery option works
5. Confirm state preserved

### Checklist
- [ ] Clear error message
- [ ] Suggests next steps
- [ ] Technical details available
- [ ] Loading state cleared
- [ ] Can retry operation
- [ ] Application still usable
- [ ] No data corruption

---

**See also:**
- `ERROR_HANDLING_AUDIT.md` - Complete error scenario coverage
- `app/utils/error_handling.py` - Implementation details
- `AGENT_3_ERROR_HANDLING_SUMMARY.md` - Implementation summary
