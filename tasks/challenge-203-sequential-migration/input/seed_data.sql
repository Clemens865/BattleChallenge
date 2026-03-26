-- Seed data for project management system
-- 50 rows across all tables

-- Teams (4 rows)
INSERT INTO teams (id, name, description) VALUES (1, 'Engineering', 'Software engineering team');
INSERT INTO teams (id, name, description) VALUES (2, 'Design', 'Product design team');
INSERT INTO teams (id, name, description) VALUES (3, 'Marketing', 'Marketing and growth team');
INSERT INTO teams (id, name, description) VALUES (4, 'Operations', 'Infrastructure and operations');

-- Users (8 rows)
INSERT INTO users (id, name, email, role, team_id) VALUES (1, 'Alice Johnson', 'alice@example.com', 'admin', 1);
INSERT INTO users (id, name, email, role, team_id) VALUES (2, 'Bob Smith', 'bob@example.com', 'manager', 1);
INSERT INTO users (id, name, email, role, team_id) VALUES (3, 'Carol White', 'carol@example.com', 'member', 1);
INSERT INTO users (id, name, email, role, team_id) VALUES (4, 'David Brown', 'david@example.com', 'manager', 2);
INSERT INTO users (id, name, email, role, team_id) VALUES (5, 'Eve Davis', 'eve@example.com', 'member', 2);
INSERT INTO users (id, name, email, role, team_id) VALUES (6, 'Frank Wilson', 'frank@example.com', 'manager', 3);
INSERT INTO users (id, name, email, role, team_id) VALUES (7, 'Grace Lee', 'grace@example.com', 'member', 3);
INSERT INTO users (id, name, email, role, team_id) VALUES (8, 'Henry Taylor', 'henry@example.com', 'member', 4);

-- Projects (5 rows)
INSERT INTO projects (id, name, description, status, team_id) VALUES (1, 'Website Redesign', 'Complete overhaul of company website', 'active', 1);
INSERT INTO projects (id, name, description, status, team_id) VALUES (2, 'Mobile App v2', 'Next generation mobile application', 'active', 1);
INSERT INTO projects (id, name, description, status, team_id) VALUES (3, 'Brand Refresh', 'Update brand guidelines and assets', 'active', 2);
INSERT INTO projects (id, name, description, status, team_id) VALUES (4, 'Q1 Campaign', 'First quarter marketing campaign', 'completed', 3);
INSERT INTO projects (id, name, description, status, team_id) VALUES (5, 'Infrastructure Upgrade', 'Cloud migration and scaling', 'active', 4);

-- Tasks (12 rows)
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (1, 'Design homepage mockup', 'Create Figma mockups for new homepage', 'done', 'high', 1, 5, 4, '2026-02-15', 16);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (2, 'Implement responsive layout', 'Build responsive CSS grid layout', 'in_progress', 'high', 1, 3, 2, '2026-03-01', 24);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (3, 'Set up CI/CD pipeline', 'Configure GitHub Actions for deployment', 'done', 'critical', 1, 1, 1, '2026-01-20', 8);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (4, 'API authentication', 'Implement JWT-based auth system', 'in_progress', 'critical', 2, 2, 1, '2026-03-15', 32);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (5, 'Push notifications', 'Integrate Firebase push notifications', 'open', 'medium', 2, 3, 2, '2026-04-01', 20);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (6, 'Logo redesign', 'Create new logo variants', 'in_progress', 'high', 3, 5, 4, '2026-02-28', 40);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (7, 'Style guide document', 'Write comprehensive style guide', 'open', 'medium', 3, 4, 4, '2026-03-30', 24);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (8, 'Social media content', 'Create social media post templates', 'done', 'medium', 4, 7, 6, '2026-01-15', 12);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (9, 'Email campaign', 'Design and send Q1 newsletter', 'done', 'high', 4, 6, 6, '2026-01-31', 8);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (10, 'Kubernetes migration', 'Migrate services to K8s cluster', 'in_progress', 'critical', 5, 8, 1, '2026-04-15', 80);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (11, 'Database optimization', 'Index tuning and query optimization', 'open', 'high', 5, 1, 8, '2026-03-20', 16);
INSERT INTO tasks (id, title, description, status, priority, project_id, assigned_to, created_by, due_date, estimated_hours) VALUES (12, 'Write unit tests', 'Achieve 80% code coverage', 'blocked', 'medium', 2, 3, 2, '2026-03-10', 30);

-- Comments (10 rows)
INSERT INTO comments (id, body, task_id, author_id) VALUES (1, 'Looking great! Just a few tweaks needed on the header.', 1, 4);
INSERT INTO comments (id, body, task_id, author_id) VALUES (2, 'I''ve updated the color scheme per feedback.', 1, 5);
INSERT INTO comments (id, body, task_id, author_id) VALUES (3, 'The grid layout is working well on mobile.', 2, 3);
INSERT INTO comments (id, body, task_id, author_id) VALUES (4, 'Can we add dark mode support too?', 2, 2);
INSERT INTO comments (id, body, task_id, author_id) VALUES (5, 'Pipeline is green, all tests passing.', 3, 1);
INSERT INTO comments (id, body, task_id, author_id) VALUES (6, 'Using RS256 for JWT signing. Thoughts?', 4, 2);
INSERT INTO comments (id, body, task_id, author_id) VALUES (7, 'RS256 is good. Make sure to rotate keys quarterly.', 4, 1);
INSERT INTO comments (id, body, task_id, author_id) VALUES (8, 'Three logo variants attached for review.', 6, 5);
INSERT INTO comments (id, body, task_id, author_id) VALUES (9, 'Campaign metrics look promising so far.', 9, 7);
INSERT INTO comments (id, body, task_id, author_id) VALUES (10, 'Need to resolve dependency issues before proceeding.', 12, 3);

-- Attachments (6 rows)
INSERT INTO attachments (id, filename, file_size, mime_type, comment_id, uploaded_by) VALUES (1, 'homepage_v1.fig', 2048000, 'application/figma', 1, 5);
INSERT INTO attachments (id, filename, file_size, mime_type, comment_id, uploaded_by) VALUES (2, 'homepage_v2.fig', 2150000, 'application/figma', 2, 5);
INSERT INTO attachments (id, filename, file_size, mime_type, comment_id, uploaded_by) VALUES (3, 'mobile_screenshot.png', 450000, 'image/png', 3, 3);
INSERT INTO attachments (id, filename, file_size, mime_type, comment_id, uploaded_by) VALUES (4, 'logo_variant_a.svg', 12000, 'image/svg+xml', 8, 5);
INSERT INTO attachments (id, filename, file_size, mime_type, comment_id, uploaded_by) VALUES (5, 'logo_variant_b.svg', 11500, 'image/svg+xml', 8, 5);
INSERT INTO attachments (id, filename, file_size, mime_type, comment_id, uploaded_by) VALUES (6, 'logo_variant_c.svg', 13200, 'image/svg+xml', 8, 5);

-- Audit Log (5 rows)
INSERT INTO audit_log (id, action, entity_type, entity_id, user_id, details) VALUES (1, 'create', 'project', 1, 1, 'Created project: Website Redesign');
INSERT INTO audit_log (id, action, entity_type, entity_id, user_id, details) VALUES (2, 'create', 'task', 1, 4, 'Created task: Design homepage mockup');
INSERT INTO audit_log (id, action, entity_type, entity_id, user_id, details) VALUES (3, 'update', 'task', 1, 5, 'Changed status from open to done');
INSERT INTO audit_log (id, action, entity_type, entity_id, user_id, details) VALUES (4, 'create', 'task', 10, 1, 'Created task: Kubernetes migration');
INSERT INTO audit_log (id, action, entity_type, entity_id, user_id, details) VALUES (5, 'delete', 'comment', 99, 1, 'Removed spam comment');
