# bardclean - Command-Line Interface & Validation
<!-- File: /home/mlj/utono/bardclean/TASKS-02.md -->

## Milestone 2: Command-Line Interface & Validation (6-10 hours)

This milestone enhances the command-line interface with validation mode,
dry-run preview, and standardized exit codes. These features enable safe
exploration of file contents before modification.

**Priority:** P1 (Important - Required for safe batch operations)

**Dependencies:**
- Milestone 1 (File Type Detection) must be complete
- Requires FileTypeFeatures and detect_file_type() from Phase 1.1

**Deliverables:**
- Enhanced argument parser with new flags
- Validation mode with structured output
- Dry-run preview mode
- Standard exit code system

---

## Phase 2.1: Argument Parser Enhancement (FR-7 from PRD.md)

### Overview
Expand the argument parser to support new modes and flags for validation,
dry-run, and agent integration.

**Estimated time:** 2-3 hours

### Tasks

- [2.1.1] [X] Add validation mode arguments
  a. Add --validate flag: "Check file structure and type"
  b. Add --stats-only flag: "Analyze without processing"
  c. Store in args.validate and args.stats_only
  d. Make mutually exclusive with processing flags
  e. Update help text with examples

- [2.1.2] [X] Add preview and safety arguments
  a. Add --dry-run flag: "Preview changes without modifying files"
  b. Add --no-backup flag: "Skip backup creation (agents only)"
  c. Add --force flag: "Override poetry protection (not recommended)"
  d. Store in args.dry_run, args.no_backup, args.force
  e. Add warning in help text for --force

- [2.1.3] [X] Add output control arguments
  a. Add --verbose / -v flag: "Detailed output"
  b. Add --quiet / -q flag: "Minimal output"
  c. Add --json flag: "Output results as JSON"
  d. Make --quiet and --verbose mutually exclusive
  e. Store verbosity level in args

- [2.1.4] [ ] Add file type override argument
  a. Add --file-type TYPE argument
  b. Choices: auto, play, narrative, poetry
  c. Default to 'auto' (use detection)
  d. Allow override for edge cases
  e. Document when override is appropriate

- [2.1.5] [X] Improve help text and examples
  a. Add usage examples to help output
  b. Show interactive selection example
  c. Show validation example
  d. Show dry-run example
  e. Show agent-friendly batch example
  f. Add version information with --version

### Verification Checklist
- [ ] All new arguments parse correctly
- [ ] Help text is clear and comprehensive
- [ ] Mutually exclusive groups work properly
- [ ] Flag combinations make sense (no conflicting flags)
- [ ] Examples in help text are accurate

---

## Phase 2.2: Validation Mode Implementation (FR-9 from PRD.md)

### Overview
Implement validation mode that analyzes file structure and provides
recommendations without modifying files. Critical for agent workflows.

**Estimated time:** 3-4 hours

### Tasks

- [2.2.1] [X] Create ValidationResult dataclass
  a. Add is_shakespeare_file: bool field
  b. Add detected_type: str field
  c. Add confidence: float field
  d. Add is_processable: bool field
  e. Add processing_mode: str field (dialogue, quoted, none)
  f. Add features: FileTypeFeatures field
  g. Add warnings: List[str] field
  h. Add recommendation: str field

- [2.2.2] [X] Implement validate_file() function
  a. Read file content
  b. Call extract_features() from Phase 1.1
  c. Call detect_file_type() with features
  d. Determine if file is processable
  e. Generate processing mode recommendation
  f. Create list of warnings based on file type
  g. Return ValidationResult instance

- [2.2.3] [X] Add Shakespeare file detection
  a. Check for Project Gutenberg header
  b. Check for "by William Shakespeare"
  c. Check for typical Shakespeare structures
  d. Set is_shakespeare_file based on checks
  e. Warn if file doesn't appear to be Shakespeare

- [2.2.4] [X] Implement processability logic
  a. Play: processable=True, mode="dialogue"
  b. Narrative poem: processable=True, mode="quoted", add warning
  c. Sonnet: processable=False, mode="none", explain why
  d. Lyric: processable=False, mode="none", explain why
  e. Unknown: processable=False, mode="none", suggest --file-type

- [2.2.5] [X] Create recommendation text generator
  a. Play: "Safe to process as play"
  b. Narrative: "Processable with caution - quoted dialogue only"
  c. Sonnet: "Not recommended - pure poetry, use --force to override"
  d. Lyric: "Not recommended - pure poetry, use --force to override"
  e. Unknown: "Cannot determine file type - specify with --file-type"

- [2.2.6] [X] Add character name extraction
  a. Extract all unique character names
  b. Store in features.character_names
  c. Include count in validation output
  d. Show first 10 character names as sample
  e. Estimate dialogue lines based on character count

- [2.2.7] [X] Implement validation output formatting
  a. Create format_validation_result() for human output
  b. Show file type with confidence score
  c. Display key features (character count, stage directions, etc.)
  d. List warnings if any
  e. Show recommendation prominently
  f. Make output colorful if terminal supports it

### Verification Checklist
- [ ] Validation mode works without modifying files
- [ ] Correctly validates all Shakespeare file types
- [ ] Character names extracted accurately
- [ ] Confidence scores reflect detection certainty
- [ ] Recommendations are clear and actionable
- [ ] Warnings appear for edge cases
- [ ] Non-Shakespeare files detected and flagged

---

## Phase 2.3: Dry-Run Preview Mode

### Overview
Implement dry-run mode that shows what would be changed without actually
modifying files. Useful for users to preview results.

**Estimated time:** 2-3 hours

### Tasks

- [2.3.1] [X] Add dry_run flag to DialogueProcessor
  a. Add self.dry_run = False in __init__
  b. Accept dry_run parameter in constructor
  c. Check dry_run before file write operations
  d. Skip backup creation in dry-run mode
  e. Skip permission modifications in dry-run mode

- [2.3.2] [X] Implement change preview tracking
  a. Create ChangePreview dataclass
  b. Fields: line_number, original, modified, change_type
  c. Track all changes during dry-run
  d. Store in self.preview_changes list
  e. Limit preview to first 50 changes to avoid huge output

- [2.3.3] [X] Add preview output formatting
  a. Create format_preview() method
  b. Show total changes count
  c. Display first 10-20 changes as examples
  d. Use diff-style format: - original / + modified
  e. Show punctuation removal summary
  f. Indicate if more changes exist

- [2.3.4] [X] Test dry-run mode thoroughly
  a. Verify no files are modified
  b. Verify no backups are created
  c. Verify permissions unchanged
  d. Verify preview output is accurate
  e. Compare dry-run output with actual processing

- [2.3.5] [X] Add dry-run summary statistics
  a. Count total lines that would be modified
  b. Count total punctuation marks to be removed
  c. Estimate processing time
  d. Show "Run without --dry-run to apply changes" message
  e. Include file type and confidence in summary

### Verification Checklist
- [ ] Dry-run never modifies files
- [ ] Preview shows accurate changes
- [ ] Summary statistics are correct
- [ ] No backups created in dry-run mode
- [ ] No permission changes in dry-run mode
- [ ] Clear indication that changes were not applied

---

## Phase 2.4: Exit Code Standardization (FR-10 from PRD.md)

### Overview
Implement standard exit codes for reliable error handling by scripts and agents.
Critical for automation workflows.

**Estimated time:** 1-2 hours

### Tasks

- [2.4.1] [X] Create ExitCode enumeration
  a. Define ExitCode class with standard codes
  b. SUCCESS = 0: All files processed successfully
  c. GENERAL_ERROR = 1: Unspecified error occurred
  d. FILE_NOT_FOUND = 2: Input file doesn't exist
  e. PERMISSION_ERROR = 3: Cannot read/write file
  f. INVALID_FORMAT = 4: File is not processable Shakespeare text
  g. VALIDATION_FAILED = 5: File failed validation checks
  h. NO_FILES = 6: Empty file list
  i. USER_CANCELLED = 7: Interactive selection cancelled

- [2.4.2] [X] Update error handling to use exit codes
  a. Replace sys.exit(1) with sys.exit(ExitCode.GENERAL_ERROR)
  b. Use FILE_NOT_FOUND for missing files
  c. Use PERMISSION_ERROR for permission issues
  d. Use INVALID_FORMAT for poetry files (without --force)
  e. Use VALIDATION_FAILED for failed validation
  f. Use NO_FILES when no files selected
  g. Use USER_CANCELLED for fzf cancellation

- [2.4.3] [X] Add exit code to processing results
  a. Include exit_code in result dictionary
  b. Set based on success/failure status
  c. Use most severe exit code if multiple files
  d. Document exit code meanings in help text
  e. Include exit code in JSON output

- [2.4.4] [X] Test all exit code scenarios
  a. Test successful processing → 0
  b. Test file not found → 2
  c. Test permission denied → 3
  d. Test poetry file without --force → 4
  e. Test validation failure → 5
  f. Test empty file list → 6
  g. Test cancelled selection → 7

### Verification Checklist
- [X] All exit codes defined in ExitCode class
- [X] All exit points use proper exit codes
- [X] Exit codes match PRD.md specification
- [ ] Help text documents exit codes
- [X] JSON output includes exit code
- [X] Multiple file processing uses most severe code

---

## Phase 2.5: Main Flow Integration

### Overview
Integrate all new features into the main processing flow with proper mode
detection and routing.

**Estimated time:** 1-2 hours

### Tasks

- [2.5.1] [X] Implement mode detection in main()
  a. Check args.validate → call validation mode
  b. Check args.dry_run → enable dry-run flag
  c. Check args.stats_only → enable stats-only mode
  d. Set verbosity level based on --quiet/-v
  e. Route to appropriate processing mode

- [2.5.2] [X] Create validation mode main flow
  a. Parse file arguments
  b. Call validate_file() for each file
  c. Collect ValidationResult objects
  d. Format output (human or JSON based on --json)
  e. Return appropriate exit code
  f. Don't process files, only validate

- [2.5.3] [X] Update regular processing flow
  a. Pass dry_run flag to DialogueProcessor
  b. Pass force flag to DialogueProcessor
  c. Pass no_backup flag to DialogueProcessor
  d. Respect verbosity settings
  e. Use proper exit codes

- [2.5.4] [X] Add file argument validation
  a. Check files exist before processing
  b. Check files are readable
  c. Provide clear error for missing files
  d. Use FILE_NOT_FOUND exit code
  e. Continue with remaining files in batch

- [2.5.5] [X] Improve error messages
  a. Include file path in all error messages
  b. Suggest solutions for common errors
  c. Use consistent formatting
  d. Add color for warnings/errors if terminal supports
  e. Make errors actionable

### Verification Checklist
- [ ] Mode detection works correctly
- [ ] Validation mode never processes files
- [ ] Dry-run mode never modifies files
- [ ] File validation catches missing files early
- [ ] Error messages are clear and helpful
- [ ] All modes work with multiple files

---

## Milestone 2: Overall Verification

### Functional Requirements Coverage
- [x] FR-7: Command-Line Interface enhanced
- [x] FR-9: Validation Mode implemented
- [x] FR-10: Exit Codes standardized

### Testing Requirements for Milestone 2
- [ ] Test --validate with all file types
- [ ] Test --dry-run shows accurate preview
- [ ] Test all exit codes with appropriate scenarios
- [ ] Test argument combinations (--validate --json, etc.)
- [ ] Test with missing files
- [ ] Test with invalid file types
- [ ] Test batch processing with mixed file types
- [ ] Test mutually exclusive argument groups

### Success Metrics
- [ ] Validation mode provides accurate file type detection
- [ ] Dry-run mode never modifies files
- [ ] All 8 exit codes work correctly
- [ ] Help text is comprehensive and clear
- [ ] Error messages guide users to solutions
- [ ] Validation output includes all required information

### Documentation Requirements
- [ ] Document all new flags in --help
- [ ] Add examples for each mode to README.md
- [ ] Document exit codes in agent_usage.md
- [ ] Add validation workflow examples
- [ ] Document dry-run use cases

---

## Next Steps

After completing Milestone 2, proceed to TASKS-03.md (Agent Integration & JSON
Output) which builds on validation mode and exit codes to provide full agent
integration capabilities.
