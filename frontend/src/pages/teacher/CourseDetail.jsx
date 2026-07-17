import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox, EmptyState, PageHeader } from '../../components/ui.jsx'

export default function CourseDetail() {
  const { id } = useParams()
  const qc = useQueryClient()

  const course = useQuery({
    queryKey: ['course', id],
    queryFn: async () => (await api.get(`/courses/${id}/`)).data,
  })

  const invalidate = () => qc.invalidateQueries({ queryKey: ['course', id] })

  const addModule = useMutation({
    mutationFn: (body) => api.post(`/courses/${id}/modules/`, body),
    onSuccess: invalidate,
  })

  if (course.isLoading) return <Spinner />
  if (course.isError) return <ErrorBox error={course.error} />

  const data = course.data
  const modules = data.modules || []

  return (
    <div>
      <PageHeader
        title={data.title}
        subtitle={data.description}
        actions={
          <Link to="/t" className="btn-secondary">
            ← Dashboard
          </Link>
        }
      />

      <AddModule
        onAdd={(title) => addModule.mutate({ title, order: modules.length + 1 })}
        pending={addModule.isPending}
      />
      {addModule.isError && <ErrorBox error={addModule.error} />}

      <div className="mt-6 space-y-6">
        {modules.length ? (
          modules.map((mod) => (
            <ModuleCard key={mod.id} module={mod} onChanged={invalidate} />
          ))
        ) : (
          <EmptyState title="No modules yet" hint="Add a module to organise resources." />
        )}
      </div>
    </div>
  )
}

function AddModule({ onAdd, pending }) {
  const [title, setTitle] = useState('')
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (!title.trim()) return
        onAdd(title.trim())
        setTitle('')
      }}
      className="card flex flex-wrap items-end gap-3"
    >
      <div className="flex-1">
        <label className="label">New module</label>
        <input
          className="input"
          placeholder="Module title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
      <button className="btn-primary" disabled={pending}>
        Add module
      </button>
    </form>
  )
}

function ModuleCard({ module, onChanged }) {
  const qc = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(module.title)

  const updateModule = useMutation({
    mutationFn: (body) => api.patch(`/modules/${module.id}/`, body),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })
  const deleteModule = useMutation({
    mutationFn: () => api.delete(`/modules/${module.id}/`),
    onSuccess: onChanged,
  })
  const addResource = useMutation({
    mutationFn: (body) => api.post(`/modules/${module.id}/resources/`, body),
    onSuccess: onChanged,
  })

  const resources = module.resources || []

  return (
    <div className="card">
      <div className="flex items-center justify-between gap-2">
        {editing ? (
          <input
            className="input max-w-sm"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        ) : (
          <h3 className="text-lg font-semibold text-slate-800">{module.title}</h3>
        )}
        <div className="flex gap-2">
          {editing ? (
            <>
              <button
                className="btn-primary"
                onClick={() => updateModule.mutate({ title })}
                disabled={updateModule.isPending}
              >
                Save
              </button>
              <button className="btn-secondary" onClick={() => setEditing(false)}>
                Cancel
              </button>
            </>
          ) : (
            <>
              <button className="btn-secondary" onClick={() => setEditing(true)}>
                Rename
              </button>
              <button
                className="btn-danger"
                onClick={() => {
                  if (confirm('Delete this module?')) deleteModule.mutate()
                }}
              >
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {resources.map((r) => (
          <ResourceRow key={r.id} resource={r} onChanged={onChanged} />
        ))}
        {!resources.length && (
          <p className="text-sm text-slate-500">No resources in this module.</p>
        )}
      </div>

      <AddResource
        onAdd={(body) => addResource.mutate({ ...body, order: resources.length + 1 })}
        pending={addResource.isPending}
      />
    </div>
  )
}

function ResourceRow({ resource, onChanged }) {
  const del = useMutation({
    mutationFn: () => api.delete(`/resources/${resource.id}/`),
    onSuccess: onChanged,
  })
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
      <div className="flex items-center justify-between">
        <p className="font-medium text-slate-800">{resource.title}</p>
        <button
          className="text-sm text-red-600 hover:underline"
          onClick={() => del.mutate()}
        >
          Remove
        </button>
      </div>
      {resource.text_body && (
        <p className="mt-1 whitespace-pre-wrap text-sm text-slate-600">{resource.text_body}</p>
      )}
    </div>
  )
}

function AddResource({ onAdd, pending }) {
  const [title, setTitle] = useState('')
  const [textBody, setTextBody] = useState('')
  const [open, setOpen] = useState(false)

  if (!open) {
    return (
      <button className="mt-3 text-sm font-medium text-brand-600 hover:underline" onClick={() => setOpen(true)}>
        + Add resource
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (!title.trim()) return
        onAdd({ title: title.trim(), text_body: textBody })
        setTitle('')
        setTextBody('')
        setOpen(false)
      }}
      className="mt-3 space-y-2 rounded-md border border-dashed border-slate-300 p-3"
    >
      <input
        className="input"
        placeholder="Resource title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        className="input"
        rows={3}
        placeholder="Text body"
        value={textBody}
        onChange={(e) => setTextBody(e.target.value)}
      />
      <div className="flex gap-2">
        <button className="btn-primary" disabled={pending}>
          Save resource
        </button>
        <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>
          Cancel
        </button>
      </div>
    </form>
  )
}
