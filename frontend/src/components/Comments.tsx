import { useState, type FormEvent } from "react";

import { formatWhen, type Comment } from "../types";

interface CommentsProps {
  comments: Comment[];
  canComment: boolean;
  onSubmit: (content: string) => Promise<void>;
}

export function Comments({ comments, canComment, onSubmit }: CommentsProps) {
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setPending(true);
    try {
      await onSubmit(content);
      setContent("");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not add comment");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="stack">
      <h2>Comments</h2>
      {comments.length === 0 && <p className="muted">No comments yet.</p>}
      <ul className="comment-list">
        {comments.map((comment) => (
          <li key={comment.id} className="comment">
            <div className="comment-meta">
              <strong>{comment.author_name}</strong>
              <span>{formatWhen(comment.created_at)}</span>
            </div>
            <p>{comment.content}</p>
          </li>
        ))}
      </ul>
      {canComment ? (
        <form className="stack" onSubmit={handleSubmit}>
          <label>
            Add a comment
            <textarea
              value={content}
              onChange={(event) => setContent(event.target.value)}
              maxLength={5000}
              required
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button" type="submit" disabled={pending}>
            {pending ? "Sending…" : "Send comment"}
          </button>
        </form>
      ) : (
        <p className="muted">Comments are closed for this ticket.</p>
      )}
    </section>
  );
}
