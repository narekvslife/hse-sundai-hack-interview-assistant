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
  async function updateSolution(language, pageHTML) {
    // Show loading state
    solutionDisplay.classList.add('processing');
    solutionDisplay.textContent = '';
    solutionDisplay.textContent = 'Generating solution...';
    
    const apiLanguage = language;
    
    // Create form data for the API request
    const formData = new FormData();
    formData.append('task', pageHTML);
    formData.append('programming_language', apiLanguage);
    
    // Make API call to the backend
    try {
      const response = await fetch('http://84.252.131.206:8000/upload', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'text/plain'
        },
        body: formData
      });

      console.log("Status:", response.status, "Status Text:", response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error details:", errorText);
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText} - ${errorText}`);
      }

      // Check for streaming response
      if (!response.body) {
        throw new Error("ReadableStream not available.");
      }

      // Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let receivedText = '';
      let firstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        const chunkText = decoder.decode(value, { stream: true });
        receivedText += chunkText;

        if (firstChunk) {
          // Clear the 'Generating...' message on first chunk
          solutionDisplay.textContent = '';
          firstChunk = false;
        }

        // Update the display incrementally
        solutionDisplay.textContent = receivedText;

        // Optional: Add syntax highlighting class here if needed later
        solutionDisplay.className = 'code-display python'; 
      }
      
      // Handle case where stream completes but is empty
      if (firstChunk) {
        solutionDisplay.textContent = '// No solution generated.';
      }

    } catch (error) {
      console.error('Fetch error:', error);
      solutionDisplay.textContent = `Error generating solution: ${error.message}`;
    } finally {
      // Remove loading state
      solutionDisplay.classList.remove('processing');
    }
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