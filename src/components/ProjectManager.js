import React, { useEffect, useState, useCallback } from 'react';
import { format } from 'date-fns';
const ipc = window.electron ? window.electron : null;

const ProjectManager = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      const result = ipc ? await ipc.invoke('get-projects') : [];
      setProjects(result);
      setError(null);
    } catch (err) {
      setError(`Failed to load projects: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <div className="project-manager">
      {loading && <p>Loading projects...</p>}
      {error && <p className="error-message">{error}</p>}
      {projects.length === 0 ? <p>No projects found.</p> : (
        <ul>
          {projects.map((project) => (
            <li key={project.id}>
              {project.name} - Created: {format(new Date(project.created_at), 'MMM dd, yyyy')}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ProjectManager;