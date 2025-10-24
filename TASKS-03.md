# bardclean - Agent Integration & JSON Output
<!-- File: /home/mlj/utono/bardclean/TASKS-03.md -->

## Milestone 3: Agent Integration & JSON Output (10-14 hours)

This milestone implements the JSON output system and programmatic API that
enable coding agents and automation scripts to reliably use bardclean. This is
the critical milestone that unblocks agent integration.

**Priority:** P0 (Critical - Enables all agent/automation workflows)

**Dependencies:**
- Milestone 1 (File Type Detection) must be complete
- Milestone 2 (Validation Mode & Exit Codes) must be complete
- Requires FileStructureMetadata from Phase 1.5

**Deliverables:**
- Complete JSON output schema implementation
- Programmatic Python API
- Batch processing with type filtering
- Comprehensive statistics tracking

---

## Phase 3.1: JSON Output Schema (FR-8 from PRD.md)

### Overview
Implement comprehensive JSON output mode that provides structured,
machine-readable results for agent consumption. This is the highest-priority
feature blocking agent integration.

**Estimated time:** 4-5 hours

### Tasks

- [3.1.1] [X] Create ProcessingResult dataclass
  a. Add filepath: str field
  b. Add status: str field (success, error, skipped)
  c. Add file_type: dict field (detected, confidence)
  d. Add processing: dict field (total_lines, modified_lines, etc.)
  e. Add changes: dict field (punctuation_removed counts)
  f. Add backup_created: Optional[str] field
  g. Add permissions_restored: bool field
  h. Add warnings: List[str] field
  i. Add error: Optional[dict] field

- [3.1.2] [X] Create BatchResult dataclass
  a. Add status: str field (success, partial, error)
  b. Add exit_code: int field
  c. Add timestamp: str field (ISO format)
  d. Add files_processed: int field
  e. Add files_failed: int field
  f. Add files_skipped: int field
  g. Add results: List[ProcessingResult] field
  h. Add summary: dict field (aggregate statistics)

- [3.1.3] [X] Implement JSON serialization methods
  a. Add to_dict() method on ProcessingResult
  b. Add to_dict() method on BatchResult
  c. Add to_json() method that returns JSON string
  d. Use json.dumps() with indent=2 for readability
  e. Handle datetime serialization properly
  f. Handle None values gracefully

- [3.1.4] [X] Implement punctuation counting
  a. Create PunctuationStats dataclass
  b. Fields: commas, semicolons, colons, exclamations, quotes, dashes
  c. Add count_punctuation() method
  d. Count removed punctuation during processing
  e. Include in ProcessingResult.changes
  f. Add total_removed field

- [3.1.5] [X] Add processing statistics tracking
  a. Track total_lines in file
  b. Track dialogue_lines (lines in dialogue mode)
  c. Track modified_lines (lines with changes)
  d. Track unchanged_lines (lines without changes)
  e. Track skipped_lines (metadata, stage directions, etc.)
  f. Include all stats in ProcessingResult.processing

- [3.1.6] [X] Implement JSON output formatting
  a. Create format_json_output() function
  b. Accept BatchResult or ProcessingResult
  c. Convert to dict, then to JSON
  d. Validate JSON structure before output
  e. Handle encoding issues
  f. Write to stdout or file

- [3.1.7] [X] Add --json flag integration
  a. Check args.json in main()
  b. Collect all ProcessingResult objects
  c. Create BatchResult with summary
  d. Output JSON instead of human text
  e. Ensure no human-readable text mixed in

- [3.1.8] [X] Test JSON output with all scenarios
  a. Test single file success
  b. Test multiple files success
  c. Test file with errors
  d. Test mixed success/failure batch
  e. Test with validation mode
  f. Test with dry-run mode
  g. Verify JSON is valid and parsable

### Verification Checklist
- [ ] JSON output matches schema from PRD.md:331-376
- [ ] All fields populated correctly
- [ ] JSON is valid (parsable by json.loads())
- [ ] Punctuation counts are accurate
- [ ] Statistics match actual processing
- [ ] Error information is comprehensive
- [ ] Timestamp is ISO 8601 format
- [ ] Exit code included in output

---

## Phase 3.2: Programmatic Python API

### Overview
Refactor code to support both CLI and programmatic usage, enabling agents to
import and use bardclean as a Python library.

**Estimated time:** 3-4 hours

### Tasks

- [3.2.1] [ ] Refactor main() for library usage
  a. Separate argument parsing from logic
  b. Create process_files() function
  c. Accept parameters instead of args
  d. Return ProcessingResult objects
  e. Don't call sys.exit() in library mode
  f. Raise exceptions instead

- [3.2.2] [ ] Create public API functions
  a. Create validate_file(filepath) -> ValidationResult
  b. Create process_file(filepath, **options) -> ProcessingResult
  c. Create process_files(filepaths, **options) -> BatchResult
  d. Create generate_metadata(filepath) -> FileStructureMetadata
  e. Document parameters and return types
  f. Add type hints to all functions

- [3.2.3] [ ] Add options parameter handling
  a. Accept dry_run, force, no_backup as kwargs
  b. Accept verbose, quiet as kwargs
  c. Accept file_type override as kwarg
  d. Validate option combinations
  e. Provide sensible defaults

- [3.2.4] [ ] Create exception hierarchy
  a. Base: BardCleanError(Exception)
  b. FileNotFoundError subclass
  c. PermissionError subclass
  d. InvalidFileFormatError subclass (for poetry)
  e. ValidationError subclass
  f. Include file path in all exceptions

- [3.2.5] [ ] Add library-friendly logging
  a. Use Python logging module
  b. Don't print to stdout in library mode
  c. Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
  d. Allow caller to configure logging
  e. Provide logger name: 'bardclean'

- [3.2.6] [ ] Create __init__.py for package
  a. Export main API functions
  b. Export result dataclasses
  c. Export exception classes
  d. Define __all__ list
  e. Add version number
  f. Add docstring with usage example

- [3.2.7] [ ] Test programmatic usage
  a. Import as module: from bardclean import process_file
  b. Test all API functions
  c. Test exception handling
  d. Test with various option combinations
  e. Verify no stdout pollution

### Verification Checklist
- [ ] Can import: from bardclean import process_file
- [ ] All public functions have type hints
- [ ] All public functions have docstrings
- [ ] Exceptions provide useful information
- [ ] No sys.exit() calls in library mode
- [ ] Logging configurable by caller
- [ ] API is intuitive and well-documented

---

## Phase 3.3: Batch Processing Safety

### Overview
Implement safe batch processing that auto-detects file types and filters
appropriately, preventing accidental poetry processing.

**Estimated time:** 2-3 hours

### Tasks

- [3.3.1] [ ] Create batch file type filtering
  a. Add filter_by_type() function
  b. Accept list of filepaths
  c. Return dict: {type: [files]}
  d. Separate plays, narratives, poetry
  e. Log filtering summary

- [3.3.2] [ ] Implement safe batch mode
  a. Add --safe-batch flag
  b. Auto-filter to processable files only
  c. Skip poetry files automatically
  d. Log skipped files with reasons
  e. Provide summary of what was processed

- [3.3.3] [ ] Add batch processing options
  a. Add --continue-on-error flag
  b. Continue processing if one file fails
  c. Collect all errors for summary
  d. Use most severe exit code
  e. Report success/failure counts

- [3.3.4] [ ] Implement parallel processing (optional)
  a. Add --parallel flag (optional feature)
  b. Use multiprocessing for large batches
  c. Process independent files in parallel
  d. Collect results safely
  e. Maintain deterministic ordering

- [3.3.5] [ ] Add batch statistics aggregation
  a. Sum total_lines across files
  b. Sum modified_lines across files
  c. Aggregate punctuation_removed counts
  d. Calculate batch averages
  e. Include in BatchResult.summary

- [3.3.6] [ ] Test batch processing
  a. Test with all plays (38 files)
  b. Test with mixed types (plays + poetry)
  c. Test with --safe-batch filtering
  d. Test error handling with invalid files
  e. Test summary statistics accuracy

### Verification Checklist
- [ ] Batch mode processes multiple files correctly
- [ ] File type filtering works accurately
- [ ] Poetry files automatically skipped in safe mode
- [ ] Errors in one file don't stop batch
- [ ] Summary statistics are accurate
- [ ] JSON output includes all batch results

---

## Phase 3.4: Statistics & Metrics Enhancement

### Overview
Enhance statistics tracking and reporting to provide comprehensive insights
into processing results for analysis and optimization.

**Estimated time:** 2-3 hours

### Tasks

- [3.4.1] [X] Enhance punctuation statistics
  a. Count each punctuation type separately
  b. Track before/after punctuation density
  c. Calculate percentage reduced
  d. Track average punctuation per line
  e. Include in JSON output

- [3.4.2] [ ] Add character-level statistics (optional)
  a. Track characters removed count
  b. Track characters preserved count
  c. Calculate file size reduction percentage
  d. Include in processing result
  e. Make optional (--detailed-stats flag)

- [3.4.3] [ ] Add performance metrics
  a. Track processing time per file
  b. Track lines per second
  c. Track total processing time for batch
  d. Include in JSON output
  e. Add --benchmark flag for detailed timing

- [3.4.4] [ ] Create statistics summary report
  a. Format human-readable summary
  b. Show totals for batch processing
  c. Show averages and percentages
  d. Display in table format
  e. Make available with --stats flag

- [3.4.5] [X] Add confidence score reporting
  a. Include file type confidence in output
  b. Warn if confidence < 0.8
  c. Suggest manual review for low confidence
  d. Include confidence in JSON output
  e. Add --min-confidence threshold flag

- [3.4.6] [ ] Test statistics accuracy
  a. Verify punctuation counts manually
  b. Check statistics against test files
  c. Validate batch aggregations
  d. Test performance metrics
  e. Verify JSON structure

### Verification Checklist
- [ ] All punctuation types counted accurately
- [ ] Statistics match actual processing
- [ ] Performance metrics are reasonable
- [ ] Batch summaries aggregate correctly
- [ ] Confidence scores reflect detection quality
- [ ] JSON output includes all statistics

---

## Phase 3.5: Agent Usage Documentation

### Overview
Create comprehensive documentation specifically for coding agents, including
API examples, JSON schemas, and integration patterns.

**Estimated time:** 2-3 hours

### Tasks

- [3.5.1] [X] Create agent_usage.md documentation
  a. Document JSON output schema with examples
  b. Document all exit codes
  c. Provide Python API examples
  d. Show batch processing workflows
  e. Include error handling patterns
  f. Add integration examples

- [3.5.2] [X] Add JSON schema definitions
  a. Document ProcessingResult schema
  b. Document BatchResult schema
  c. Document ValidationResult schema
  d. Document FileStructureMetadata schema
  e. Provide schema version information

- [3.5.3] [X] Create agent workflow examples
  a. Example: Validate before processing
  b. Example: Batch process all plays
  c. Example: Filter by file type
  d. Example: Error handling and retry
  e. Example: Parse JSON output

- [3.5.4] [X] Add CLI examples for agents
  a. Validation workflow
  b. Dry-run workflow
  c. Safe batch processing
  d. JSON output parsing
  e. Exit code handling

- [3.5.5] [X] Create integration examples
  a. Python script integration
  b. Shell script integration
  c. CI/CD pipeline integration
  d. Error handling examples
  e. Best practices section

- [3.5.6] [X] Document agent-specific flags
  a. --json: Structured output
  b. --validate: Pre-processing check
  c. --dry-run: Preview mode
  d. --no-backup: Skip backup creation
  e. --safe-batch: Auto-filter by type
  f. --continue-on-error: Batch resilience

### Verification Checklist
- [ ] agent_usage.md is comprehensive
- [ ] All JSON schemas documented
- [ ] Code examples are tested and work
- [ ] Workflows cover common use cases
- [ ] Best practices are clear
- [ ] Documentation is agent-friendly (parsable)

---

## Milestone 3: Overall Verification

### Functional Requirements Coverage
- [x] FR-8: JSON Output Schema implemented
- [x] Phase 3 from planning.md: Programmatic API created

### Testing Requirements for Milestone 3
- [ ] Test JSON output with all file types
- [ ] Test API from Python scripts
- [ ] Test batch processing with 38 plays
- [ ] Test error scenarios and JSON error output
- [ ] Test statistics accuracy
- [ ] Test all agent workflows from documentation
- [ ] Validate JSON against schema
- [ ] Test programmatic exception handling

### Success Metrics
- [ ] JSON output is valid and complete
- [ ] Python API is usable and well-documented
- [ ] Batch processing handles 38+ files reliably
- [ ] Statistics are accurate and comprehensive
- [ ] Agent documentation is clear and complete
- [ ] All exit codes work in JSON mode
- [ ] No data loss in any scenario

### Documentation Requirements
- [ ] Complete agent_usage.md with examples
- [ ] Document JSON schemas thoroughly
- [ ] Add API reference to documentation
- [ ] Include integration examples
- [ ] Update README.md with API usage
- [ ] Add troubleshooting section for agents

### Agent Integration Verification
- [ ] Can validate files programmatically
- [ ] Can process files with structured output
- [ ] Can filter files by type
- [ ] Can handle errors without crashes
- [ ] Can parse all JSON output successfully
- [ ] Can integrate into automation workflows

---

## Next Steps

After completing Milestone 3, proceed to TASKS-04.md (Testing, Documentation &
Polish) which adds comprehensive test coverage and final polish for production
release.
