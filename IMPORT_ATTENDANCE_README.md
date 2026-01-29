# Attendance Import Script

This Django management command imports attendance data from an Excel file.

## File Format

The Excel file should have the following structure:

### Sheet Names
Each sheet should be named after a batch (e.g., "Batch 1", "Batch 2", etc.). The sheet name must match a batch in the system.

### Header Structure

**Row 1 (Headers):**
```
Sr No. | Full Name | Roll No. | Branch | Present | Absent | Attendance | 15-12-2025 | 16-12-2025 | 17-12-2025 | ...
```

**Row 2 (Sub-headers):**
```
       |           |          |        |         |        |            | Morning Session | Afternoon Session | Morning Session | Afternoon Session | ...
```

**Row 3+ (Student Data):**
Each row contains:
- Sr No.: Sequential number
- Full Name: Student full name
- Roll No.: Student roll number (must exist in system)
- Branch: Branch name
- Present: Count of present days
- Absent: Count of absent days
- Attendance: Attendance percentage
- Columns 8+: Attendance status for each date/session
  - "P" or "Present" = Student was present
  - "A" or "Absent" = Student was absent
  - "Holiday" or blank cells = Skipped (no lecture created)

## Usage

### Basic Import
```bash
python manage.py import_attendance /path/to/attendance_file.xlsx
```

### Import with Record Clearing
To clear all existing attendance records and lectures before importing:
```bash
python manage.py import_attendance /path/to/attendance_file.xlsx --clear
```

## Features

- ✅ Reads multiple sheets (one per batch)
- ✅ Automatically creates Lecture records for each date and session type
- ✅ Marks attendance using student roll numbers
- ✅ Handles holidays (skips creating lectures)
- ✅ Creates system user if it doesn't exist
- ✅ Validates students exist in the batch
- ✅ Uses `update_or_create` to avoid duplicates
- ✅ Supports multiple date formats (DD-MM-YYYY, DD/MM/YYYY, DD-MMM-YYYY, etc.)

## Prerequisites

1. Batches must already exist in the system with matching names
2. Students must already exist in the system with correct roll numbers and batch assignments
3. openpyxl library must be installed (already in requirements.txt)

## Example Excel Structure

```
Sr No. | Full Name          | Roll No. | Branch | Present | Absent | Attendance | 15-12-2025        | 16-12-2025        | 17-12-2025
       |                    |          |        |         |        |            | Morning | Afternoon | Morning | Afternoon | Morning
1      | John Doe           | 22CS1001 | CSE    | 2       | 0      | 100%       | P       | P         | P       | P         | P
2      | Jane Smith         | 22CS1002 | CSE    | 1       | 1      | 50%        | A       | P         | P       | A         | Holiday
```

## Notes

- Date columns should use standard date formats (DD-MM-YYYY, DD/MM/YYYY, or DD-MMM-YYYY)
- Session type must be either "Morning Session" or "Afternoon Session" (case-insensitive)
- Using `--clear` will delete ALL attendance records and lectures before importing
- The script creates/updates lectures only for non-holiday dates
- Attendance records are created only for marked sessions (P or A)
- A system user "system_import" is automatically created to track imports
