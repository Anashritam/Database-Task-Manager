create table if not exists projects(
    id integer primary key,
    name text not null check(length(trim(name))>0),
   created_at text not null default current_timestamp
);

create table if not exists tasks(
    id integer primary key,
    project_id integer not null,
    title text not null check(length(trim(title))>0),
    description text,
    status text not null default 'todo' check(status in ('todo', 'in_progress','done')),
    priority text not null default 'medium' check(priority in ('low','medium','high','urgent')),
    due_date text,
    created_at text not null default current_timestamp,
    foreign key (project_id) references projects(id)
);