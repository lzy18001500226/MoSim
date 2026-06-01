'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUserStore } from '@/store/useUserStore';
import { AVATARS } from '@/lib/objects';

const GRADES = ['K', '1', '2', '3', '4', '5'];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [avatar, setAvatar] = useState('');
  const [name, setName] = useState('');
  const [grade, setGrade] = useState('');

  const canAdvance =
    (step === 1 && avatar !== '') ||
    (step === 2 && name.trim() !== '') ||
    (step === 3 && grade !== '');

  function handleNext() {
    if (!canAdvance) return;
    if (step < 3) {
      setStep(step + 1);
    } else {
      useUserStore.getState().createUser(name.trim(), avatar, grade);
      router.push('/create');
    }
  }

  function handleBack() {
    if (step > 1) setStep(step - 1);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500 p-4">
      <div className="child-card w-full max-w-lg text-center animate-slide-up">
        {/* Progress dots */}
        <div className="flex items-center justify-center gap-3 mb-8">
          {[1, 2, 3].map((dot) => (
            <div
              key={dot}
              className={`w-4 h-4 rounded-full transition-all duration-300 ${
                dot === step
                  ? 'bg-primary scale-125'
                  : dot < step
                    ? 'bg-primary-light'
                    : 'bg-border'
              }`}
            />
          ))}
        </div>

        {/* Step content */}
        <div key={step} className="animate-slide-up">
          {step === 1 && (
            <>
              <h1 className="text-3xl font-extrabold text-foreground mb-2">
                Pick your avatar!
              </h1>
              <p className="text-lg text-muted mb-6">
                Choose the one that looks like you
              </p>
              <div className="grid grid-cols-4 gap-4 mb-8">
                {AVATARS.map((emoji) => (
                  <button
                    key={emoji}
                    onClick={() => setAvatar(emoji)}
                    className={`w-20 h-20 mx-auto flex items-center justify-center text-4xl rounded-full border-4 transition-all duration-200 cursor-pointer hover:scale-110 active:scale-95 ${
                      avatar === emoji
                        ? 'border-primary bg-primary-light/30 scale-110'
                        : 'border-border bg-surface hover:border-primary-light'
                    }`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <h1 className="text-3xl font-extrabold text-foreground mb-2">
                What&#39;s your name?
              </h1>
              <p className="text-lg text-muted mb-6">
                Tell us what to call you
              </p>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleNext();
                }}
                placeholder="Type your name..."
                autoFocus
                className="w-full text-2xl font-bold text-center py-4 px-6 rounded-2xl border-3 border-border bg-surface focus:border-primary focus:outline-none transition-colors mb-8"
              />
            </>
          )}

          {step === 3 && (
            <>
              <h1 className="text-3xl font-extrabold text-foreground mb-2">
                What grade are you in?
              </h1>
              <p className="text-lg text-muted mb-6">
                Pick your grade level
              </p>
              <div className="grid grid-cols-3 gap-4 mb-8">
                {GRADES.map((g) => (
                  <button
                    key={g}
                    onClick={() => setGrade(g)}
                    className={`py-5 text-2xl font-extrabold rounded-2xl border-4 transition-all duration-200 cursor-pointer hover:scale-105 active:scale-95 ${
                      grade === g
                        ? 'border-primary bg-primary-light/30 text-primary'
                        : 'border-border bg-surface text-foreground hover:border-primary-light'
                    }`}
                  >
                    {g === 'K' ? 'K' : `${g}`}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Navigation buttons */}
        <div className="flex items-center justify-between gap-4">
          {step > 1 ? (
            <button
              onClick={handleBack}
              className="child-button border-border bg-surface text-foreground hover:bg-surface-hover"
            >
              Back
            </button>
          ) : (
            <div />
          )}
          <button
            onClick={handleNext}
            disabled={!canAdvance}
            className={`child-button child-button-primary ${
              !canAdvance ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {step === 3 ? 'Start Building!' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}
