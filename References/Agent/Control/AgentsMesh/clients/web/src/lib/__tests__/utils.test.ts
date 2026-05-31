import { describe, it, expect } from 'vitest'
import { cn } from '../utils'

describe('cn utility function', () => {
  describe('basic functionality', () => {
    it('should return empty string for no arguments', () => {
      expect(cn()).toBe('')
    })

    it('should return single class', () => {
      expect(cn('foo')).toBe('foo')
    })

    it('should join multiple classes', () => {
      expect(cn('foo', 'bar')).toBe('foo bar')
    })

    it('should filter out falsy values', () => {
      expect(cn('foo', null, 'bar', undefined, false, 'baz')).toBe('foo bar baz')
    })
  })

  describe('conditional classes', () => {
    it('should handle conditional object syntax', () => {
      expect(cn({ foo: true, bar: false })).toBe('foo')
    })

    it('should handle mixed syntax', () => {
      expect(cn('base', { active: true, disabled: false })).toBe('base active')
    })

    it('should handle multiple conditional objects', () => {
      expect(cn({ a: true }, { b: true }, { c: false })).toBe('a b')
    })
  })

  describe('array handling', () => {
    it('should handle array of classes', () => {
      expect(cn(['foo', 'bar'])).toBe('foo bar')
    })

    it('should handle nested arrays', () => {
      expect(cn(['foo', ['bar', 'baz']])).toBe('foo bar baz')
    })

    it('should handle mixed array and strings', () => {
      expect(cn('base', ['one', 'two'], 'three')).toBe('base one two three')
    })
  })

  describe('tailwind merge functionality', () => {
    it('should merge conflicting padding classes', () => {
      expect(cn('px-4', 'px-6')).toBe('px-6')
    })

    it('should merge conflicting margin classes', () => {
      expect(cn('mt-2', 'mt-4')).toBe('mt-4')
    })

    it('should merge conflicting text color classes', () => {
      expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500')
    })

    it('should merge conflicting background classes', () => {
      expect(cn('bg-red-500', 'bg-blue-500')).toBe('bg-blue-500')
    })

    it('should merge conflicting width classes', () => {
      expect(cn('w-4', 'w-8')).toBe('w-8')
    })

    it('should merge conflicting height classes', () => {
      expect(cn('h-4', 'h-8')).toBe('h-8')
    })

    it('should keep non-conflicting classes', () => {
      expect(cn('px-4', 'py-2', 'mt-4')).toBe('px-4 py-2 mt-4')
    })

    it('should handle rounded classes', () => {
      expect(cn('rounded', 'rounded-lg')).toBe('rounded-lg')
    })

    it('should handle flex classes', () => {
      expect(cn('flex', 'flex-col')).toBe('flex flex-col')
    })

    it('should handle display classes', () => {
      expect(cn('block', 'flex')).toBe('flex')
    })
  })

  describe('real-world use cases', () => {
    it('should handle button variant classes', () => {
      const baseClasses = 'px-4 py-2 rounded bg-blue-500 text-white'
      const variantClasses = 'bg-red-500'
      expect(cn(baseClasses, variantClasses)).toBe('px-4 py-2 rounded text-white bg-red-500')
    })

    it('should handle conditional disabled state', () => {
      const isDisabled = true
      expect(cn('btn', { 'opacity-50 cursor-not-allowed': isDisabled })).toBe(
        'btn opacity-50 cursor-not-allowed'
      )
    })

    it('should handle responsive classes', () => {
      expect(cn('w-full', 'md:w-1/2', 'lg:w-1/3')).toBe('w-full md:w-1/2 lg:w-1/3')
    })

    it('should handle hover and focus states', () => {
      expect(cn('bg-blue-500', 'hover:bg-blue-600', 'focus:ring-2')).toBe(
        'bg-blue-500 hover:bg-blue-600 focus:ring-2'
      )
    })

    it('should handle className override pattern', () => {
      const defaultClasses = 'px-4 py-2 bg-primary'
      const userClasses = 'px-6 bg-secondary'
      // User classes should override defaults
      expect(cn(defaultClasses, userClasses)).toBe('py-2 px-6 bg-secondary')
    })
  })

  describe('edge cases', () => {
    it('should handle empty string', () => {
      expect(cn('')).toBe('')
    })

    it('should handle only whitespace', () => {
      expect(cn('   ')).toBe('')
    })

    it('should handle number zero', () => {
      expect(cn('foo', 0 as unknown as string)).toBe('foo')
    })

    it('should not deduplicate identical non-tailwind classes', () => {
      // clsx doesn't deduplicate, only tailwind-merge does for conflicting utility classes
      expect(cn('foo', 'foo')).toBe('foo foo')
    })
  })
})
