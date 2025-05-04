document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const languageButtons = document.querySelectorAll('.lang-btn');
  const solutionDisplay = document.getElementById('solution-display');
  const copyButton = document.getElementById('copy-btn');
  const regenerateButton = document.getElementById('regenerate-btn');
  
  // Current selected language (default: JavaScript)
  let currentLanguage = 'js';
  
  // Sample solutions for demo purposes
  const sampleSolutions = {
    js: `function twoSum(nums, target) {
  const map = new Map();
  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];
    if (map.has(complement)) {
      return [map.get(complement), i];
    }
    map.set(nums[i], i);
  }
  return [];
}`,
    python: `def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []`,
    java: `public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (map.containsKey(complement)) {
            return new int[] { map.get(complement), i };
        }
        map.put(nums[i], i);
    }
    return new int[0];
}`,
    cpp: `vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> map;
    for (int i = 0; i < nums.size(); i++) {
        int complement = target - nums[i];
        if (map.count(complement)) {
            return {map[complement], i};
        }
        map[nums[i]] = i;
    }
    return {};
}`
  };
  
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
  
  // Regenerate solution (in a real app, this would call your solution generation service)
  regenerateButton.addEventListener('click', function() {
    // Add animation to show processing
    solutionDisplay.classList.add('processing');
    
    // Simulate API call with timeout
    setTimeout(() => {
      // TODO: Call your solution generation API here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      // In a real implementation, this would be replaced with actual API call
      updateSolution(currentLanguage);
      solutionDisplay.classList.remove('processing');
    }, 1000);
  });
  
  // Function to update solution based on language
  function updateSolution(language) {
    solutionDisplay.textContent = sampleSolutions[language] || '// No solution available';
    
    // Update the comment style based on language
    if (language === 'js' || language === 'java' || language === 'cpp') {
      solutionDisplay.className = 'code-display ' + language;
    } else if (language === 'python') {
      solutionDisplay.className = 'code-display python';
    }
  }
  
  // Store language preference
  function savePreference() {
    chrome.storage.sync.set({ preferredLanguage: currentLanguage });
  }
  
  // Load language preference if available
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
}); 