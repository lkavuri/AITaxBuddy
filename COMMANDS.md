# 🚀 AI Tax Buddy Commands

Your AI Tax Buddy now has simple commands like `claude`!

## 🔧 One-Time Setup

Run the install script to make commands available globally:

```bash
cd /Users/lkavuri/aitaxbuddy
./install.sh

# Then restart your terminal or run:
source ~/.zshrc  # or source ~/.bashrc
```

Now you can use `taxbuddy` or `aitax` from anywhere!

## Available Commands

You can use either `taxbuddy` or `aitax` (they're the same):

### Start Interactive Chat
```bash
taxbuddy chat
# or
aitax chat
```

### Ask a Single Question
```bash
taxbuddy query "Can I claim my home office expenses?"
# or
aitax query "What is the tax-free threshold?"
```

### Run Tests
```bash
taxbuddy evaluate
```

### Show Configuration
```bash
taxbuddy info
```

### Get Help
```bash
taxbuddy --help
```

## 🎨 What It Looks Like

When you run `taxbuddy chat`, you'll see a beautiful terminal UI:

```
╔════════════════════════════════════════════╗
║         🇦🇺 AI Tax Buddy                  ║
║                                            ║
║    Australian Tax Guidance Agent           ║
║    ⚠️  General Advice Only                ║
╚════════════════════════════════════════════╝

You > Can I claim my home office expenses?

Tax Buddy is thinking... ⠋

╭──────────── 💼 Tax Buddy ────────────╮
│                                       │
│ Yes! Home office expenses are...     │
│                                       │
╰───────────────────────────────────────╯
```

## 🔧 Setup (One Time)

After installing, activate your environment:

```bash
cd /Users/lkavuri/aitaxbuddy
source venv/bin/activate
```

Now you can use `taxbuddy` or `aitax` from anywhere!

## 💡 Pro Tips

**Alias for Even Shorter Commands:**

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias tb='taxbuddy'
alias tax='aitax'
```

Then just use:
```bash
tb chat
tax query "your question"
```

**Always Active (Advanced):**

To make commands available without activating venv:

```bash
# Add this to your ~/.zshrc or ~/.bashrc
export PATH="/Users/lkavuri/aitaxbuddy/venv/bin:$PATH"
```

Then `taxbuddy` works from anywhere, anytime!

## 📱 Example Session

```bash
$ taxbuddy chat

You > I earned $80,000. How much tax will I pay?

Tax Buddy > [Calculates and explains tax bracket...]

You > Can I claim travel between home and work?

Tax Buddy > [Explains commuting is not deductible + warning...]

You > exit

Thanks for chatting! Remember to lodge by October 31! 🇦🇺
```

## 🎯 All Options

```bash
# Start chat
taxbuddy chat [--user-id YOUR_ID]

# Single query
taxbuddy query "your question" [--user-id YOUR_ID]

# Run tests
taxbuddy evaluate

# Show config
taxbuddy info

# Get help
taxbuddy --help
```

The `--user-id` option lets you have separate conversation histories for different users!

---

**Enjoy your AI Tax Buddy!** 🇦🇺✨
