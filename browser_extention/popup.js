document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const languageButtons = document.querySelectorAll('.lang-btn');
  const solutionDisplay = document.getElementById('solution-display');
  // const copyButton = document.getElementById('copy-btn');
  // const regenerateButton = document.getElementById('regenerate-btn');
  const container = document.querySelector('.container');
  const problemTextArea = document.getElementById('problem-text');
  
  // Current selected language (default: JavaScript)
  let currentLanguage = 'python';

  // Function to be injected into the active tab to get HTML
  function getContentScript() {
    return document.documentElement.outerHTML;
  }

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
    });
  });
  
  // Function to update solution based on language and page HTML
  function updateSolution(language, pageHTML) {
    // Show loading state
    solutionDisplay.classList.add('processing');
    solutionDisplay.textContent = 'Generating solution...';
    
    const apiLanguage = language;
    
    // Create form data for the API request
    const formData = new FormData();
    // Get the problem text from the textarea
    // const problemText = problemTextArea.value.trim() || 'No solution';
    formData.append('task', pageHTML);
    formData.append('programming_language', apiLanguage);
    
    // Make API call to the backend
    fetch('http://84.252.131.206:8000/upload', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Accept': 'application/json'
      },
      body: formData
    })
    .then(response => {
      console.log("Status:", response.status, "Status Text:", response.statusText);
      if (!response.ok) {
        return response.text().then(text => {
          console.error("Error details:", text);
          throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
        });
      }
      return response.json();
    })
    .then(data => {
      // Update the solution with the LLM response
      solutionDisplay.textContent = data.llm_response || '// No solution available';
      
      // Update the comment style based on language
      solutionDisplay.className = 'code-display python';
    })
    .finally(() => {
      // Remove loading state
      solutionDisplay.classList.remove('processing');
    });
  }
  
  // Function to get page HTML and then call updateSolution
  function getPageHTMLAndSolve(language) {
    if (chrome && chrome.tabs && chrome.scripting) {
      chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        if (tabs.length === 0) {
          console.error("No active tab found.");
          solutionDisplay.textContent = 'Error: Could not find active tab.';
          return;
        }
        const tabId = tabs[0].id;
        
        chrome.scripting.executeScript(
          {
            target: { tabId: tabId },
            func: getContentScript,
          },
          (injectionResults) => {
            if (chrome.runtime.lastError) {
              console.error("Script injection failed: ", chrome.runtime.lastError.message);
              solutionDisplay.textContent = `Error: Could not access page content (${chrome.runtime.lastError.message}). Try reloading the page or the extension.`;
              solutionDisplay.classList.remove('processing');
              return;
            }
            
            if (injectionResults && injectionResults.length > 0 && injectionResults[0].result) {
              const pageHTML = injectionResults[0].result;
              updateSolution(language, pageHTML); // Call updateSolution with the HTML
            } else {
              console.error("Failed to get page HTML. Injection result:", injectionResults);
              solutionDisplay.textContent = 'Error: Could not retrieve page content.';
              solutionDisplay.classList.remove('processing');
            }
          }
        );
      });
    } else {
      console.error("Chrome APIs (tabs or scripting) not available.");
      solutionDisplay.textContent = 'Error: Chrome APIs not available.';
    }
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
      getPageHTMLAndSolve(currentLanguage); // Call the new function
    }
  }

}); 