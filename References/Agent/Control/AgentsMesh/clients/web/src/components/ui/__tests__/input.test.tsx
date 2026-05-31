import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Input } from '../input'

describe('Input Component', () => {
  describe('rendering', () => {
    it('should render input element', () => {
      render(<Input />)
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('should render with placeholder', () => {
      render(<Input placeholder="Enter text" />)
      expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
    })

    it('should render with value', () => {
      render(<Input value="test value" readOnly />)
      expect(screen.getByDisplayValue('test value')).toBeInTheDocument()
    })
  })

  describe('types', () => {
    it('should render text input by default', () => {
      render(<Input />)
      const input = screen.getByRole('textbox')
      // When type is not explicitly set, it defaults to text (implicit)
      expect(input.getAttribute('type') || 'text').toBe('text')
    })

    it('should render email input', () => {
      render(<Input type="email" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'email')
    })

    it('should render password input', () => {
      render(<Input type="password" />)
      // Password inputs don't have textbox role
      const input = document.querySelector('input[type="password"]')
      expect(input).toBeInTheDocument()
    })

    it('should render number input', () => {
      render(<Input type="number" />)
      const input = screen.getByRole('spinbutton')
      expect(input).toHaveAttribute('type', 'number')
    })

    it('should render search input', () => {
      render(<Input type="search" />)
      const input = screen.getByRole('searchbox')
      expect(input).toHaveAttribute('type', 'search')
    })
  })

  describe('error state', () => {
    it('should show error message when error prop is provided', () => {
      render(<Input error="This field is required" />)
      expect(screen.getByText('This field is required')).toBeInTheDocument()
    })

    it('should apply error styles to input', () => {
      render(<Input error="Error" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('border-destructive')
    })

    it('should apply error ring styles on focus', () => {
      render(<Input error="Error" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('focus-visible:ring-destructive')
    })

    it('should not show error message when no error', () => {
      render(<Input />)
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument()
    })

    it('should render error message with correct styling', () => {
      render(<Input error="Error message" />)
      const errorText = screen.getByText('Error message')
      expect(errorText).toHaveClass('text-xs')
      expect(errorText).toHaveClass('text-destructive')
    })
  })

  describe('disabled state', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Input disabled />)
      const input = screen.getByRole('textbox')
      expect(input).toBeDisabled()
    })

    it('should apply disabled styles', () => {
      render(<Input disabled />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('disabled:cursor-not-allowed')
      expect(input).toHaveClass('disabled:opacity-50')
    })
  })

  describe('events', () => {
    it('should call onChange when value changes', () => {
      const handleChange = vi.fn()
      render(<Input onChange={handleChange} />)
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'new value' } })
      expect(handleChange).toHaveBeenCalledTimes(1)
    })

    it('should call onFocus when focused', () => {
      const handleFocus = vi.fn()
      render(<Input onFocus={handleFocus} />)
      const input = screen.getByRole('textbox')
      fireEvent.focus(input)
      expect(handleFocus).toHaveBeenCalledTimes(1)
    })

    it('should call onBlur when blurred', () => {
      const handleBlur = vi.fn()
      render(<Input onBlur={handleBlur} />)
      const input = screen.getByRole('textbox')
      fireEvent.focus(input)
      fireEvent.blur(input)
      expect(handleBlur).toHaveBeenCalledTimes(1)
    })

    it('should call onKeyDown when key is pressed', () => {
      const handleKeyDown = vi.fn()
      render(<Input onKeyDown={handleKeyDown} />)
      const input = screen.getByRole('textbox')
      fireEvent.keyDown(input, { key: 'Enter' })
      expect(handleKeyDown).toHaveBeenCalledTimes(1)
    })
  })

  describe('className prop', () => {
    it('should apply custom className', () => {
      render(<Input className="custom-class" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('custom-class')
    })

    it('should merge custom className with base classes', () => {
      render(<Input className="mt-4" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('mt-4')
      expect(input).toHaveClass('flex')
      expect(input).toHaveClass('rounded-md')
    })
  })

  describe('ref forwarding', () => {
    it('should forward ref to input element', () => {
      const ref = { current: null as HTMLInputElement | null }
      render(<Input ref={ref} />)
      expect(ref.current).toBeInstanceOf(HTMLInputElement)
    })

    it('should allow focusing via ref', () => {
      const ref = { current: null as HTMLInputElement | null }
      render(<Input ref={ref} />)
      ref.current?.focus()
      expect(document.activeElement).toBe(ref.current)
    })
  })

  describe('HTML attributes', () => {
    it('should pass through name attribute', () => {
      render(<Input name="email" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('name', 'email')
    })

    it('should pass through id attribute', () => {
      render(<Input id="email-input" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('id', 'email-input')
    })

    it('should pass through aria attributes', () => {
      render(<Input aria-label="Email address" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-label', 'Email address')
    })

    it('should pass through required attribute', () => {
      render(<Input required />)
      const input = screen.getByRole('textbox')
      expect(input).toBeRequired()
    })

    it('should pass through maxLength attribute', () => {
      render(<Input maxLength={100} />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('maxLength', '100')
    })

    it('should pass through autoComplete attribute', () => {
      render(<Input autoComplete="email" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('autocomplete', 'email')
    })

    it('should pass through data attributes', () => {
      render(<Input data-testid="test-input" />)
      expect(screen.getByTestId('test-input')).toBeInTheDocument()
    })
  })

  describe('wrapper element', () => {
    it('should render wrapper div with full width', () => {
      const { container } = render(<Input />)
      const wrapper = container.firstChild
      expect(wrapper).toHaveClass('w-full')
    })
  })
})
