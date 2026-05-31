import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PromoCodeInput } from './PromoCodeInput'
import * as promocodeConnect from '@/lib/api/facade/promocodeConnect'

const mockT = (key: string) => {
  const translations: Record<string, string> = {
    placeholder: 'Enter promo code',
    validate: 'Validate',
    validating: 'Validating...',
    redeem: 'Redeem',
    redeeming: 'Redeeming...',
    enterCode: 'Please enter a promo code',
    invalid: 'Invalid promo code',
    validateError: 'Failed to validate promo code',
    redeemError: 'Failed to redeem promo code',
    valid: 'Valid promo code',
    plan: 'Plan',
    duration: 'Duration',
    months: 'months',
    confirmRedeem: 'Click redeem to activate',
    'errors.promo_code_not_found': 'Promo code not found',
    'errors.promo_code_not_owner': 'Only owner can redeem',
  }
  return translations[key] || key
}

vi.mock('@/lib/api/facade/promocodeConnect', () => ({
  validatePromoCode: vi.fn(),
  redeemPromoCode: vi.fn(),
  getRedemptionHistory: vi.fn(),
}))

const ORG_SLUG = 'acme'

describe('PromoCodeInput', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders input and validate button', () => {
    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    expect(screen.getByPlaceholderText('Enter promo code')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Validate' })).toBeInTheDocument()
  })

  it('converts input to uppercase', async () => {
    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'test123')
    expect(input).toHaveValue('TEST123')
  })

  it('disables validate button when code is empty', () => {
    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const button = screen.getByRole('button', { name: 'Validate' })
    expect(button).toBeDisabled()
  })

  it('validates promo code successfully', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })

    const onValidate = vi.fn()
    render(<PromoCodeInput orgSlug={ORG_SLUG} onValidate={onValidate} t={mockT} />)

    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Valid promo code')).toBeInTheDocument()
    })
    expect(screen.getByText(/Plan: Pro/)).toBeInTheDocument()
    expect(screen.getByText(/Duration: 3 months/)).toBeInTheDocument()
    expect(promocodeConnect.validatePromoCode).toHaveBeenCalledWith(ORG_SLUG, 'TEST123')
    expect(onValidate).toHaveBeenCalledWith({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })
  })

  it('shows error for invalid promo code', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: false, code: 'INVALID', messageCode: 'promo_code_not_found',
    })

    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'INVALID')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Promo code not found')).toBeInTheDocument()
    })
  })

  it('shows error on validate API failure', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockRejectedValue(new Error('Network error'))

    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Failed to validate promo code')).toBeInTheDocument()
    })
  })

  it('redeems promo code after validation', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })
    vi.mocked(promocodeConnect.redeemPromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.RedeemPromoCodeResponse",
      success: true, planName: 'pro', durationMonths: 3,
    })

    const onRedeemSuccess = vi.fn()
    render(<PromoCodeInput orgSlug={ORG_SLUG} onRedeemSuccess={onRedeemSuccess} t={mockT} />)

    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Valid promo code')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: 'Redeem' }))

    await waitFor(() => {
      expect(onRedeemSuccess).toHaveBeenCalledWith({
        $typeName: "proto.promocode.v1.RedeemPromoCodeResponse",
        success: true, planName: 'pro', durationMonths: 3,
      })
    })
    expect(promocodeConnect.redeemPromoCode).toHaveBeenCalledWith(ORG_SLUG, 'TEST123')
    expect(input).toHaveValue('')
  })

  it('shows error on redeem failure', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })
    vi.mocked(promocodeConnect.redeemPromoCode).mockRejectedValue(new Error('Redeem failed'))

    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Valid promo code')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: 'Redeem' }))

    await waitFor(() => {
      expect(screen.getByText('Failed to redeem promo code')).toBeInTheDocument()
    })
  })

  it('surfaces message_code from a non-success redeem response', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })
    vi.mocked(promocodeConnect.redeemPromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.RedeemPromoCodeResponse",
      success: false, messageCode: 'promo_code_not_owner',
    })

    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Valid promo code')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: 'Redeem' }))

    await waitFor(() => {
      expect(screen.getByText('Only owner can redeem')).toBeInTheDocument()
    })
  })

  it('disables input and button when disabled prop is true', () => {
    render(<PromoCodeInput orgSlug={ORG_SLUG} disabled={true} t={mockT} />)
    expect(screen.getByPlaceholderText('Enter promo code')).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Validate' })).toBeDisabled()
  })

  it('handles Enter key to validate', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })

    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.keyboard('{Enter}')

    await waitFor(() => {
      expect(promocodeConnect.validatePromoCode).toHaveBeenCalledWith(ORG_SLUG, 'TEST123')
    })
  })

  it('clears validation when code changes', async () => {
    vi.mocked(promocodeConnect.validatePromoCode).mockResolvedValue({
      $typeName: "proto.promocode.v1.ValidatePromoCodeResponse",
      valid: true, code: 'TEST123', planName: 'pro',
      planDisplayName: 'Pro', durationMonths: 3,
    })

    render(<PromoCodeInput orgSlug={ORG_SLUG} t={mockT} />)
    const input = screen.getByPlaceholderText('Enter promo code')
    await userEvent.type(input, 'TEST123')
    await userEvent.click(screen.getByRole('button', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('Valid promo code')).toBeInTheDocument()
    })

    await userEvent.clear(input)
    await userEvent.type(input, 'NEW')
    expect(screen.queryByText('Valid promo code')).not.toBeInTheDocument()
  })
})
