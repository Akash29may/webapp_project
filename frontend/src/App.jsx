import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import RequireRole from './auth/RequireRole.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import TeacherDashboard from './pages/teacher/TeacherDashboard.jsx'
import CourseDetail from './pages/teacher/CourseDetail.jsx'
import ExamEditor from './pages/teacher/ExamEditor.jsx'
import ExamResults from './pages/teacher/ExamResults.jsx'
import StudentDashboard from './pages/student/StudentDashboard.jsx'
import ExamRunner from './pages/student/ExamRunner.jsx'
import AttemptResult from './pages/student/AttemptResult.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Teacher */}
        <Route
          path="/t"
          element={
            <RequireRole role="teacher">
              <TeacherDashboard />
            </RequireRole>
          }
        />
        <Route
          path="/t/courses/:id"
          element={
            <RequireRole role="teacher">
              <CourseDetail />
            </RequireRole>
          }
        />
        <Route
          path="/t/exams/:id"
          element={
            <RequireRole role="teacher">
              <ExamEditor />
            </RequireRole>
          }
        />
        <Route
          path="/t/exams/:id/results"
          element={
            <RequireRole role="teacher">
              <ExamResults />
            </RequireRole>
          }
        />

        {/* Student */}
        <Route
          path="/s"
          element={
            <RequireRole role="student">
              <StudentDashboard />
            </RequireRole>
          }
        />
        <Route
          path="/s/attempts/:id/result"
          element={
            <RequireRole role="student">
              <AttemptResult />
            </RequireRole>
          }
        />
      </Route>

      {/* Exam runner is outside the standard Layout for a focused view */}
      <Route
        path="/s/exams/:id/take"
        element={
          <RequireRole role="student">
            <ExamRunner />
          </RequireRole>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
