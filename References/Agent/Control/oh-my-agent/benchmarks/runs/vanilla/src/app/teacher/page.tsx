'use client';

import { useState, useEffect } from 'react';
import { loadTeacherPrompts, saveTeacherPrompts, loadAllWorlds } from '@/lib/storage';
import { CHALLENGES } from '@/lib/ai';
import { World } from '@/types';
import { v4 as uuid } from 'uuid';
import Link from 'next/link';

interface TeacherPrompt {
  id: string;
  title: string;
  description: string;
}

export default function TeacherPage() {
  const [prompts, setPrompts] = useState<TeacherPrompt[]>([]);
  const [worlds, setWorlds] = useState<World[]>([]);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [activeTab, setActiveTab] = useState<'prompts' | 'worlds' | 'challenges'>('prompts');

  useEffect(() => {
    setPrompts(loadTeacherPrompts());
    setWorlds(loadAllWorlds());
  }, []);

  const addPrompt = () => {
    if (!newTitle.trim()) return;
    const updated = [
      ...prompts,
      { id: uuid(), title: newTitle.trim(), description: newDesc.trim() },
    ];
    setPrompts(updated);
    saveTeacherPrompts(updated);
    setNewTitle('');
    setNewDesc('');
  };

  const removePrompt = (id: string) => {
    const updated = prompts.filter((p) => p.id !== id);
    setPrompts(updated);
    saveTeacherPrompts(updated);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-blue-50">
      <header className="bg-white/80 backdrop-blur-sm border-b border-border sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="text-2xl font-black bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"
          >
            DreamWorld
          </Link>
          <span className="text-sm font-bold text-muted bg-gray-100 px-4 py-1.5 rounded-full">
            👩‍🏫 Teacher Dashboard
          </span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        <h1 className="text-3xl font-black text-foreground mb-2">
          Teacher Dashboard
        </h1>
        <p className="text-muted font-semibold mb-8">
          Manage creative prompts and monitor student creations
        </p>

        <div className="flex gap-2 mb-8">
          {(['prompts', 'worlds', 'challenges'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2 rounded-full font-bold text-sm transition-all ${
                activeTab === tab
                  ? 'bg-primary text-white shadow-md'
                  : 'bg-white text-foreground/60 hover:bg-gray-100 border border-border'
              }`}
            >
              {tab === 'prompts' ? '📝 My Prompts' : tab === 'worlds' ? '🌍 Student Worlds' : '🎯 Challenges'}
            </button>
          ))}
        </div>

        {activeTab === 'prompts' && (
          <div>
            <div className="child-card mb-6">
              <h3 className="font-bold text-lg mb-4">Create a New Prompt</h3>
              <div className="space-y-3">
                <input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="Prompt title (e.g., Build Your Dream Home)"
                  className="w-full px-4 py-3 rounded-xl border-2 border-border focus:border-primary outline-none text-sm font-semibold transition-colors"
                />
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Description and instructions for students..."
                  rows={3}
                  className="w-full px-4 py-3 rounded-xl border-2 border-border focus:border-primary outline-none text-sm font-semibold transition-colors resize-none"
                />
                <button
                  onClick={addPrompt}
                  disabled={!newTitle.trim()}
                  className="child-button child-button-primary !py-2 !px-6 !text-sm disabled:opacity-40"
                >
                  + Add Prompt
                </button>
              </div>
            </div>

            {prompts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-4xl mb-3">📝</p>
                <p className="text-muted font-bold">No prompts yet. Create one above!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {prompts.map((p) => (
                  <div key={p.id} className="child-card flex items-start justify-between">
                    <div>
                      <h4 className="font-bold text-foreground">{p.title}</h4>
                      {p.description && (
                        <p className="text-sm text-muted mt-1">{p.description}</p>
                      )}
                    </div>
                    <button
                      onClick={() => removePrompt(p.id)}
                      className="text-xs px-3 py-1 bg-danger/10 text-danger rounded-full font-bold hover:bg-danger/20 transition-colors flex-shrink-0 ml-4"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'worlds' && (
          <div>
            {worlds.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-4xl mb-3">🌍</p>
                <p className="text-muted font-bold">No student worlds yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {worlds.map((w) => (
                  <div key={w.id} className="child-card">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-bold">{w.name}</h4>
                      <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-bold">
                        {w.objects.length} objects
                      </span>
                    </div>
                    <p className="text-xs text-muted font-semibold">
                      By: {w.createdBy || 'Anonymous'} &middot; Theme: {w.theme} &middot;{' '}
                      {new Date(w.updatedAt).toLocaleDateString()}
                    </p>
                    <div className="mt-3 p-3 bg-gray-50 rounded-xl">
                      <p className="text-xs font-bold text-muted mb-1">Reflection Questions:</p>
                      <ul className="text-xs text-foreground/60 space-y-1">
                        <li>- Why did you build it this way?</li>
                        <li>- What feeling does your world show?</li>
                        <li>- What would you build next?</li>
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'challenges' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {CHALLENGES.map((ch) => (
              <div key={ch.id} className="child-card">
                <h4 className="font-bold text-lg mb-1">{ch.title}</h4>
                <p className="text-sm text-muted mb-3">{ch.description}</p>
                <div className="space-y-1">
                  {ch.prompts.map((p, i) => (
                    <p key={i} className="text-xs bg-accent/10 text-accent rounded-lg px-3 py-1.5 font-semibold">
                      💡 {p}
                    </p>
                  ))}
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-muted font-bold capitalize">
                    {ch.category} &middot; {ch.theme}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
