document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const languageButtons = document.querySelectorAll('.lang-btn');
  const solutionDisplay = document.getElementById('solution-display');
  const copyButton = document.getElementById('copy-btn');
  const regenerateButton = document.getElementById('regenerate-btn');
  const container = document.querySelector('.container');
  const problemTextArea = document.getElementById('problem-text');
  
  // Current selected language (default: JavaScript)
  let currentLanguage = 'js';
  
  // Initialize with JavaScript solution
  updateSolution(currentLanguage);
  
  // Language selection
  languageButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Update UI
      languageButtons.forEach(btn => btn.classList.remove('selected'));
      this.classList.add('selected');
      
      // Update current language
      currentLanguage = this.id;
      
      // Save the preference
      savePreference();
      
      // Update solution display
      updateSolution(currentLanguage);
    });
  });
  
  // Copy solution to clipboard
  copyButton.addEventListener('click', function() {
    navigator.clipboard.writeText(solutionDisplay.textContent)
      .then(() => {
        // Visual feedback
        const originalText = copyButton.textContent;
        copyButton.textContent = 'Copied!';
        setTimeout(() => {
          copyButton.textContent = originalText;
        }, 1500);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
      });
  });
  
  // Regenerate solution
  regenerateButton.addEventListener('click', function() {
    // Call the updateSolution function to fetch from API
    updateSolution(currentLanguage);
  });
  
  // Function to update solution based on language
  function updateSolution(language) {
    // Show loading state
    solutionDisplay.classList.add('processing');
    solutionDisplay.textContent = 'Generating solution...';
    
    const apiLanguage = language;
    
    // Create form data for the API request
    const formData = new FormData();
    // Get the problem text from the textarea
    const problemText = problemTextArea.value.trim() || 'No solution';
    formData.append('task', problemText);
    formData.append('programming_language', apiLanguage);
    
    // Make API call to the backend
    fetch('http://84.252.131.206:8000/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'application/json'
      },
      mode: 'no-cors'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      console.log("response was ok ");
      console.log(response);
      return response.json();
    })
    .then(data => {
      // Update the solution with the LLM response
      solutionDisplay.textContent = data.llm_response || '// No solution available';
      
      // Update the comment style based on language
      if (language === 'js' || language === 'java' || language === 'cpp') {
        solutionDisplay.className = 'code-display ' + language;
      } else if (language === 'python') {
        solutionDisplay.className = 'code-display python';
      }
    })
    .catch(error => {
      console.error('Error fetching solution:', error);
      solutionDisplay.textContent = '// Error: Could not generate solution. Using fallback.';
      // Fallback to sample solutions if API call fails
    })
    .finally(() => {
      // Remove loading state
      solutionDisplay.classList.remove('processing');
    });
  }
  
  // Store language preference
  function savePreference() {
    if (chrome && chrome.storage) {
      chrome.storage.sync.set({ preferredLanguage: currentLanguage });
    }
  }
  
  // Load language preference if available
  if (chrome && chrome.storage) {
    chrome.storage.sync.get('preferredLanguage', function(data) {
      if (data.preferredLanguage) {
        currentLanguage = data.preferredLanguage;
        
        // Update UI
        languageButtons.forEach(btn => {
          if (btn.id === currentLanguage) {
            btn.classList.add('selected');
          } else {
            btn.classList.remove('selected');
          }
        });
        
        updateSolution(currentLanguage);
      }
    });
  }
  
  // Add event listener for key presses - replace the existing one
  document.addEventListener('keydown', handleKeyPress);
  
  // Also add it to the solution display element for more reliable capture
  solutionDisplay.addEventListener('keydown', handleKeyPress);
  
  // And to the container element
  container.addEventListener('keydown', handleKeyPress);
  
  function handleKeyPress(event) {
    console.log('Key pressed:', event.key, 'Ctrl key:', event.ctrlKey);
    
    // Check if 'a' key is pressed
    if (event.ctrlKey || event.key === 'Control') {
      // Generate a random color
      const randomColor = getRandomColor();
      console.log('Changing color to:', randomColor);
      
      // Apply the random color to the solution text
      solutionDisplay.style.color = randomColor;
    }
  }
  
  // Function to generate a random color
  function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }
}); 