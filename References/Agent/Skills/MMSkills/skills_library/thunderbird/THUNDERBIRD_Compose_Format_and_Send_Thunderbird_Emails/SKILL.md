---
name: Compose Format and Send Thunderbird Emails
description: Create a new Thunderbird message, fill headers and body content, optionally format the body, and send it.
---

# Compose Format and Send Thunderbird Emails

## Overview

Handle the standard new-message workflow in Thunderbird: open a fresh composer, fill the headers and body, apply visible formatting when required, and send the message.

## When to Use

- Use this skill for fresh outgoing emails rather than replies, forwards, or draft edits.
- This skill ends when the compose window is ready to send or the send action is executed.

## Preconditions

- Thunderbird is open on the Mail surface or can be returned to from the current window.
- The requested mailbox, account, sender, recipient, or folder name from the task is already known.

## Atomic Capabilities

- **open_new_message**: Open a fresh compose window and fill the message headers.
- Derived from: Compose New Email
- **format_body**: Apply visible compose formatting before sending.
- Derived from: Format Email Body
- **send_message**: Send the prepared Thunderbird message.
- Derived from: Send or Save Composed Message

## Decision Guide

- If `no compose window is open yet`, choose `open_new_message`. Start from the Mail toolbar so the new composer is opened on the intended account surface.
- If `the body already exists and only visual formatting must change`, choose `format_body`. Work from the active compose window and verify the formatting in the visible editor before sending.

## Visual Annotation Conventions

- Red boxes mark the interactive target that should be clicked, typed into, or otherwise manipulated.
- Green boxes mark the state signal or result change that the agent should verify before continuing.

## Image References To Create

- `new_message_entry.png`
- `headers_ready_for_edit.png`
- `send_ready_with_visible_content.png`

## Procedures

### Open a new message, fill content, and send it

#### State-Action Mapping

##### State 1: new_message_entry

Visual grounding:
- Thunderbird Mail shows the New Message control that opens a fresh composer.
- Image reference: `Images/new_message_entry.png`

Trigger condition:
- A new outgoing message is required and no compose window is open yet.

Action:
- Click New Message to open the composer on the current mail account.

##### State 2: headers_ready_for_edit

Visual grounding:
- The compose window shows the recipient and subject fields ready for the requested message content.
- Image reference: `Images/headers_ready_for_edit.png`

Trigger condition:
- The compose window is already open and ready for the main message text.

Action:
- Fill the To and Subject fields, then enter the requested body content and visible formatting.

##### Expected Result (State 3)

Visual grounding:
- The compose toolbar shows Send while the requested content and formatting are already visible in the editor.
- Image reference: `Images/send_ready_with_visible_content.png`

Trigger condition:
- All requested content and formatting have already been entered.

## Common Failure Modes

- Opening a reply or draft flow instead of a fresh message window.
- Sending before the visible body formatting matches the task.
