Write-Host "Setting up Git repository..."
git init
git config user.name "adityasingh97"
git config user.email "r.adityasingh97@gmail.com"
git add .
git commit -m "Initial release of Stock News Summarizer with Ollama"
git branch -M main
git remote add origin https://github.com/AdityaSingh97/Stock-News-Summarizer.git
Write-Host "Repository setup complete!"
Write-Host "Now attempting to push to GitHub..."
Write-Host "You may be prompted to sign in."
git push -u origin main
Read-Host -Prompt "Press Enter to exit"
