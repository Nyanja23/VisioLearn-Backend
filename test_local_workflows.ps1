# Comprehensive local testing script for Phase 6 architecture
# Tests all 6 workflows: registration, content upload, progress logging, class management

$BASE = "http://127.0.0.1:8000/api/v1"
$headers = @{"Content-Type" = "application/json"}

Write-Host "=" * 70
Write-Host "PHASE 6 LOCAL TESTING - CLASS-BASED MULTI-SUBJECT ARCHITECTURE"
Write-Host "=" * 70

# Helper function for test logging
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Uri,
        [hashtable]$Body,
        [hashtable]$AuthHeaders = $headers
    )
    
    try {
        if ($Method -eq "GET") {
            $r = Invoke-RestMethod -Uri $Uri -Method Get -Headers $AuthHeaders
        } else {
            $r = Invoke-RestMethod -Uri $Uri -Method Post -Headers $AuthHeaders -Body ($Body | ConvertTo-Json)
        }
        Write-Host "✅ $Name" -ForegroundColor Green
        return $r
    }
    catch {
        $errMsg = $_.Exception.Message
        Write-Host "❌ $Name : $errMsg" -ForegroundColor Red
        return $null
    }
}

# PHASE 1: REGISTRATION
Write-Host "`n[PHASE 1] USER REGISTRATION" -ForegroundColor Cyan

# Register class teacher
$ct_resp = Test-Endpoint -Name "Register Class Teacher" -Method POST `
    -Uri "$BASE/auth/register/class-teacher" `
    -Body @{
        email = "teacher1@visiolearn.org"
        password = "TeacherPass123!@"
        full_name = "Ms. Jane Smith"
        class_name = "Year 9 Science"
    }

if ($ct_resp) {
    $CT_ID = $ct_resp.user_id
    $CLASS_ID = $ct_resp.class_id
    $STUDENT_CODE = $ct_resp.student_code
    $TEACHER_CODE = $ct_resp.teacher_code
    Write-Host "  📌 Class ID: $CLASS_ID"
    Write-Host "  📌 Student Code: $STUDENT_CODE"
    Write-Host "  📌 Teacher Code: $TEACHER_CODE"
}

# Register subject teacher (Biology)
$st1_resp = Test-Endpoint -Name "Register Subject Teacher (Biology)" -Method POST `
    -Uri "$BASE/auth/register/subject-teacher" `
    -Body @{
        email = "biology@visiolearn.org"
        password = "BioTeacher123!@"
        full_name = "Mr. Peter Johnson"
        teacher_code = $TEACHER_CODE
        subject_name = "Biology"
    }

if ($st1_resp) {
    $ST1_ID = $st1_resp.user_id
    $SUBJECT_BIO_ID = $st1_resp.subject_id
    Write-Host "  📌 Subject ID (Biology): $SUBJECT_BIO_ID"
}

# Register subject teacher (Chemistry) - same teacher teaches 2 subjects
$st2_resp = Test-Endpoint -Name "Register Subject Teacher (Chemistry, same teacher)" -Method POST `
    -Uri "$BASE/auth/register/subject-teacher" `
    -Body @{
        email = "chemistry@visiolearn.org"
        password = "ChemTeacher123!@"
        full_name = "Mr. Paul Wilson"
        teacher_code = $TEACHER_CODE
        subject_name = "Chemistry"
    }

if ($st2_resp) {
    $ST2_ID = $st2_resp.user_id
    $SUBJECT_CHEM_ID = $st2_resp.subject_id
    Write-Host "  📌 Subject ID (Chemistry): $SUBJECT_CHEM_ID"
}

# Register students
$s1_resp = Test-Endpoint -Name "Register Student 1" -Method POST `
    -Uri "$BASE/auth/register/student" `
    -Body @{
        email = "student1@visiolearn.org"
        password = "StudentPass123!@"
        full_name = "John Ouma"
        student_code = $STUDENT_CODE
    }

if ($s1_resp) {
    $S1_ID = $s1_resp.user_id
    Write-Host "  📌 Student 1 ID: $S1_ID"
}

$s2_resp = Test-Endpoint -Name "Register Student 2" -Method POST `
    -Uri "$BASE/auth/register/student" `
    -Body @{
        email = "student2@visiolearn.org"
        password = "StudentPass123!@"
        full_name = "Alice Nakimuli"
        student_code = $STUDENT_CODE
    }

if ($s2_resp) {
    $S2_ID = $s2_resp.user_id
    Write-Host "  📌 Student 2 ID: $S2_ID"
}

# PHASE 2: LOGIN & TOKENS
Write-Host "`n[PHASE 2] AUTHENTICATION & TOKENS" -ForegroundColor Cyan

$ct_login = Test-Endpoint -Name "Login Class Teacher" -Method POST `
    -Uri "$BASE/auth/login" `
    -Body @{
        email = "teacher1@visiolearn.org"
        password = "TeacherPass123!@"
    }

$CT_TOKEN = if ($ct_login) { $ct_login.access_token } else { $null }
$CT_HEADERS = @{"Authorization" = "Bearer $CT_TOKEN"; "Content-Type" = "application/json"}

$st1_login = Test-Endpoint -Name "Login Subject Teacher (Biology)" -Method POST `
    -Uri "$BASE/auth/login" `
    -Body @{
        email = "biology@visiolearn.org"
        password = "BioTeacher123!@"
    }

$ST1_TOKEN = if ($st1_login) { $st1_login.access_token } else { $null }
$ST1_HEADERS = @{"Authorization" = "Bearer $ST1_TOKEN"; "Content-Type" = "application/json"}

$s1_login = Test-Endpoint -Name "Login Student 1" -Method POST `
    -Uri "$BASE/auth/login" `
    -Body @{
        email = "student1@visiolearn.org"
        password = "StudentPass123!@"
    }

$S1_TOKEN = if ($s1_login) { $s1_login.access_token } else { $null }
$S1_HEADERS = @{"Authorization" = "Bearer $S1_TOKEN"; "Content-Type" = "application/json"}

# PHASE 3: CONTENT UPLOAD
Write-Host "`n[PHASE 3] CONTENT UPLOAD" -ForegroundColor Cyan

$note1_resp = Test-Endpoint -Name "Upload Biology Note 1" -Method POST `
    -Uri "$BASE/notes/upload" `
    -AuthHeaders $ST1_HEADERS `
    -Body @{
        title = "Cell Structure and Function"
        subject_id = $SUBJECT_BIO_ID
        description = "Introduction to cell biology"
        grade_level = 9
        duration_seconds = 1200
    }

$NOTE1_ID = if ($note1_resp) { $note1_resp.id } else { $null }
if ($NOTE1_ID) { Write-Host "  📌 Note 1 ID: $NOTE1_ID" }

$note2_resp = Test-Endpoint -Name "Upload Biology Note 2" -Method POST `
    -Uri "$BASE/notes/upload" `
    -AuthHeaders $ST1_HEADERS `
    -Body @{
        title = "Photosynthesis"
        subject_id = $SUBJECT_BIO_ID
        description = "How plants make food"
        grade_level = 9
        duration_seconds = 1500
    }

$NOTE2_ID = if ($note2_resp) { $note2_resp.id } else { $null }
if ($NOTE2_ID) { Write-Host "  📌 Note 2 ID: $NOTE2_ID" }

# PHASE 4: CONTENT LISTING
Write-Host "`n[PHASE 4] CONTENT LISTING" -ForegroundColor Cyan

try {
    $list_resp = Invoke-RestMethod -Uri "$BASE/notes/list" -Method Get -Headers $S1_HEADERS
    Write-Host "✅ Student lists available notes" -ForegroundColor Green
    Write-Host "  📌 Found $($list_resp.Count) note(s)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Student lists available notes: $($_.Exception.Message)" -ForegroundColor Red
}

# PHASE 5: PROGRESS LOGGING
Write-Host "`n[PHASE 5] PROGRESS LOGGING" -ForegroundColor Cyan

if ($NOTE1_ID) {
    $prog1_resp = Test-Endpoint -Name "Log progress (Note 1, 600/1200 seconds)" -Method POST `
        -Uri "$BASE/progress" `
        -AuthHeaders $S1_HEADERS `
        -Body @{
            content_id = $NOTE1_ID
            last_position_seconds = 600
            completed = $false
        }
}

if ($NOTE2_ID) {
    $prog2_resp = Test-Endpoint -Name "Log progress (Note 2, completed)" -Method POST `
        -Uri "$BASE/progress" `
        -AuthHeaders $S1_HEADERS `
        -Body @{
            content_id = $NOTE2_ID
            last_position_seconds = 1500
            completed = $true
        }
}

# PHASE 6: PROGRESS VIEWING
Write-Host "`n[PHASE 6] PROGRESS VIEWING" -ForegroundColor Cyan

try {
    $my_prog = Invoke-RestMethod -Uri "$BASE/progress/me" -Method Get -Headers $S1_HEADERS
    Write-Host "✅ Student views overall progress" -ForegroundColor Green
    Write-Host "  📌 Progress items: $($my_prog.Count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Student views overall progress: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $by_subj = Invoke-RestMethod -Uri "$BASE/progress/me/by-subject" -Method Get -Headers $S1_HEADERS
    Write-Host "✅ Student views progress by subject" -ForegroundColor Green
} catch {
    Write-Host "❌ Student views progress by subject: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $subj_prog = Invoke-RestMethod -Uri "$BASE/progress/by-subject/$SUBJECT_BIO_ID" -Method Get -Headers $ST1_HEADERS
    Write-Host "✅ Subject teacher views subject progress" -ForegroundColor Green
} catch {
    Write-Host "❌ Subject teacher views subject progress: $($_.Exception.Message)" -ForegroundColor Red
}

# PHASE 7: CLASS MANAGEMENT
Write-Host "`n[PHASE 7] CLASS MANAGEMENT" -ForegroundColor Cyan

try {
    $class_info = Invoke-RestMethod -Uri "$BASE/classes/$CLASS_ID" -Method Get -Headers $CT_HEADERS
    Write-Host "✅ Class teacher views class details" -ForegroundColor Green
} catch {
    Write-Host "❌ Class teacher views class details: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $class_students = Invoke-RestMethod -Uri "$BASE/classes/$CLASS_ID/students" -Method Get -Headers $CT_HEADERS
    Write-Host "✅ Class teacher views students" -ForegroundColor Green
    Write-Host "  📌 Students in class: $($class_students.Count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Class teacher views students: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $matrix = Invoke-RestMethod -Uri "$BASE/classes/$CLASS_ID/matrix" -Method Get -Headers $CT_HEADERS
    Write-Host "✅ Class teacher views progress matrix" -ForegroundColor Green
} catch {
    Write-Host "❌ Class teacher views progress matrix: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + "=" * 70
Write-Host "LOCAL TESTING COMPLETE" -ForegroundColor Green
Write-Host "=" * 70
Write-Host "`nKey Test Values Saved:"
Write-Host "  CLASS_ID: $CLASS_ID"
Write-Host "  ST1_ID: $ST1_ID (Biology)"
Write-Host "  ST2_ID: $ST2_ID (Chemistry)"
Write-Host "  S1_ID: $S1_ID"
Write-Host "  S2_ID: $S2_ID"
