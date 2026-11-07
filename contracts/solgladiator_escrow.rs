// SolGladiator Solana On-Chain Escrow Smart Contract (Anchor Framework)
// Program ID: SoLGLad1atorEscrow11111111111111111111111111111

use anchor_lang::prelude::*;
use anchor_lang::system_program::{transfer, Transfer};

declare_id!("SoLGLad1atorEscrow11111111111111111111111111111");

#[program]
pub mod solgladiator_escrow {
    use super::*;

    /// Initialize a duel match escrow and deposit player wagers.
    pub fn initialize_duel_escrow(
        ctx: Context<InitializeDuelEscrow>,
        match_id: String,
        wager_lamports: u64,
    ) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow_vault;
        escrow.match_id = match_id;
        escrow.fighter1 = ctx.accounts.fighter1.key();
        escrow.fighter2 = ctx.accounts.fighter2.key();
        escrow.arbiter = ctx.accounts.arbiter.key();
        escrow.wager_lamports = wager_lamports;
        escrow.total_pot_lamports = wager_lamports.checked_mul(2).unwrap();
        escrow.is_settled = false;
        escrow.bump = ctx.bumps.escrow_vault;

        // Transfer Fighter 1 wager into Escrow Vault PDA
        let cpi_context1 = CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            Transfer {
                from: ctx.accounts.fighter1.to_account_info(),
                to: ctx.accounts.escrow_vault.to_account_info(),
            },
        );
        transfer(cpi_context1, wager_lamports)?;

        // Transfer Fighter 2 wager into Escrow Vault PDA
        let cpi_context2 = CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            Transfer {
                from: ctx.accounts.fighter2.to_account_info(),
                to: ctx.accounts.escrow_vault.to_account_info(),
            },
        );
        transfer(cpi_context2, wager_lamports)?;

        emit!(DuelEscrowInitialized {
            match_id: escrow.match_id.clone(),
            total_pot: escrow.total_pot_lamports,
            vault: escrow.key(),
        });

        Ok(())
    }

    /// Settle duel escrow: releases the pot to the winner and sends protocol fee to treasury.
    pub fn settle_duel_escrow(
        ctx: Context<SettleDuelEscrow>,
        duel_digest: [u8; 32],
    ) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow_vault;
        require!(!escrow.is_settled, ErrorCode::AlreadySettled);

        let total_pot = escrow.total_pot_lamports;
        // 2% protocol fee
        let fee_lamports = total_pot.checked_mul(2).unwrap().checked_div(100).unwrap();
        let winner_payout = total_pot.checked_sub(fee_lamports).unwrap();

        // Transfer payout to winning fighter
        **ctx.accounts.escrow_vault.to_account_info().try_borrow_mut_lamports()? -= winner_payout;
        **ctx.accounts.winner.to_account_info().try_borrow_mut_lamports()? += winner_payout;

        // Transfer protocol cut to treasury
        **ctx.accounts.escrow_vault.to_account_info().try_borrow_mut_lamports()? -= fee_lamports;
        **ctx.accounts.treasury.to_account_info().try_borrow_mut_lamports()? += fee_lamports;

        escrow.is_settled = true;
        escrow.winner = ctx.accounts.winner.key();

        emit!(DuelEscrowSettled {
            match_id: escrow.match_id.clone(),
            winner: escrow.winner,
            payout: winner_payout,
            duel_digest,
        });

        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(match_id: String)]
pub struct InitializeDuelEscrow<'info> {
    #[account(
        init,
        payer = fighter1,
        space = 8 + 64 + 32 + 32 + 32 + 32 + 8 + 8 + 1 + 1,
        seeds = [b"duel_escrow", match_id.as_bytes()],
        bump
    )]
    pub escrow_vault: Account<'info, EscrowVault>,
    #[account(mut)]
    pub fighter1: Signer<'info>,
    #[account(mut)]
    pub fighter2: Signer<'info>,
    pub arbiter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct SettleDuelEscrow<'info> {
    #[account(
        mut,
        seeds = [b"duel_escrow", escrow_vault.match_id.as_bytes()],
        bump = escrow_vault.bump,
        has_one = arbiter
    )]
    pub escrow_vault: Account<'info, EscrowVault>,
    pub arbiter: Signer<'info>,
    #[account(mut)]
    /// CHECK: Validated against match winner
    pub winner: AccountInfo<'info>,
    #[account(mut)]
    /// CHECK: SolGladiator Treasury Account
    pub treasury: AccountInfo<'info>,
}

#[account]
pub struct EscrowVault {
    pub match_id: String,
    pub fighter1: Pubkey,
    pub fighter2: Pubkey,
    pub arbiter: Pubkey,
    pub winner: Pubkey,
    pub wager_lamports: u64,
    pub total_pot_lamports: u64,
    pub is_settled: bool,
    pub bump: u8,
}

#[event]
pub struct DuelEscrowInitialized {
    pub match_id: String,
    pub total_pot: u64,
    pub vault: Pubkey,
}

#[event]
pub struct DuelEscrowSettled {
    pub match_id: String,
    pub winner: Pubkey,
    pub payout: u64,
    pub duel_digest: [u8; 32],
}

#[error_code]
pub enum ErrorCode {
    #[msg("This duel escrow has already been settled.")]
    AlreadySettled,
}
