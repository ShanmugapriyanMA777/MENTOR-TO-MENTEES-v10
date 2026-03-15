-- Run this in Supabase SQL Editor before starting the app
-- Go to: https://supabase.com → Your Project → SQL Editor → Paste & Run

CREATE TABLE IF NOT EXISTS mentors (
  id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  full_name text NOT NULL,
  email text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE mentors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Mentors can read own profile"
  ON mentors FOR SELECT TO authenticated USING (auth.uid() = id);

CREATE POLICY "Mentors can update own profile"
  ON mentors FOR UPDATE TO authenticated USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

CREATE POLICY "Mentors can insert own profile"
  ON mentors FOR INSERT TO authenticated WITH CHECK (auth.uid() = id);

CREATE TABLE IF NOT EXISTS students (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mentor_id uuid NOT NULL REFERENCES mentors(id) ON DELETE CASCADE,
  student_name text NOT NULL,
  register_number text UNIQUE NOT NULL,
  phone_number text NOT NULL,
  email text NOT NULL,
  date_of_birth date NOT NULL,
  blood_group text NOT NULL,
  address text NOT NULL,
  parent_name text NOT NULL,
  parent_occupation text NOT NULL,
  parent_phone text NOT NULL,
  siblings_details text DEFAULT '',
  scholarship_details text DEFAULT '',
  hackathon_details text DEFAULT '',
  arrears_details text DEFAULT '',
  cgpa decimal(4,2) DEFAULT 0.0,
  gpa decimal(4,2) DEFAULT 0.0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE students ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Mentors can read own students"
  ON students FOR SELECT TO authenticated USING (mentor_id = auth.uid());

CREATE POLICY "Mentors can insert own students"
  ON students FOR INSERT TO authenticated WITH CHECK (mentor_id = auth.uid());

CREATE POLICY "Mentors can update own students"
  ON students FOR UPDATE TO authenticated USING (mentor_id = auth.uid()) WITH CHECK (mentor_id = auth.uid());

CREATE POLICY "Mentors can delete own students"
  ON students FOR DELETE TO authenticated USING (mentor_id = auth.uid());

CREATE INDEX IF NOT EXISTS idx_students_mentor_id ON students(mentor_id);
CREATE INDEX IF NOT EXISTS idx_students_register_number ON students(register_number);
CREATE INDEX IF NOT EXISTS idx_students_student_name ON students(student_name);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ language 'plpgsql';

CREATE TRIGGER update_mentors_updated_at BEFORE UPDATE ON mentors
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
