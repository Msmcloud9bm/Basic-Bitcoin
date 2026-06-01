/**
 * Random Joke Generator - JavaScript
 * Uses JokeAPI (https://jokeapi.dev) for fetching jokes
 */

// Configuration
const API_URL = 'https://v2.jokeapi.dev/joke';
const JOKE_CATEGORIES = ['any', 'general', 'programming', 'knock-knock'];

// State
let jokesCount = 0;
let currentJoke = null;

/**
 * Fetch a joke from the API
 */
async function getJoke() {
    const category = document.getElementById('category').value;
    const messageBox = document.getElementById('message');
    const loading = document.getElementById('loading');
    const jokeBox = document.getElementById('jokeBox');

    try {
        // Show loading state
        loading.style.display = 'block';
        jokeBox.style.display = 'none';
        messageBox.innerHTML = '';

        // Build API URL
        const url = category === 'any' 
            ? `${API_URL}/Any?type=single,twopart`
            : `${API_URL}/${encodeURIComponent(category)}?type=single,twopart`;

        // Fetch joke
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error('No jokes found for this category');
        }

        // Store joke
        currentJoke = data;

        // Display joke
        displayJoke(data);

        // Update stats
        jokesCount++;
        document.getElementById('jokesCount').textContent = jokesCount;
        document.getElementById('apiStatus').textContent = 'Connected ✓';
        document.getElementById('apiStatus').style.color = '#3c3';

        loading.style.display = 'none';
        jokeBox.style.display = 'flex';

    } catch (error) {
        loading.style.display = 'none';
        displayError(error.message);
        document.getElementById('apiStatus').textContent = 'Error ✗';
        document.getElementById('apiStatus').style.color = '#c33';
        console.error('Error fetching joke:', error);
    }
}

/**
 * Display joke in the UI
 */
function displayJoke(joke) {
    const jokeText = document.getElementById('jokeText');
    const jokeType = document.getElementById('jokeType');

    if (joke.type === 'single') {
        // Single-part joke
        jokeText.textContent = joke.joke;
    } else if (joke.type === 'twopart') {
        // Two-part joke
        jokeText.innerHTML = `
            <div style="margin-bottom: 15px;">${joke.setup}</div>
            <div style="font-style: italic; color: #764ba2;">${joke.delivery}</div>
        `;
    }

    // Show category
    jokeType.textContent = `${joke.category.toUpperCase()} • ${joke.type.toUpperCase()}`;
}

/**
 * Display error message
 */
function displayError(message) {
    const messageBox = document.getElementById('message');
    messageBox.innerHTML = `<div class="error">⚠️ ${message}</div>`;
}

/**
 * Display success message
 */
function displaySuccess(message) {
    const messageBox = document.getElementById('message');
    messageBox.innerHTML = `<div class="success">✓ ${message}</div>`;
    setTimeout(() => {
        messageBox.innerHTML = '';
    }, 3000);
}

/**
 * Copy current joke to clipboard
 */
function copyJoke() {
    if (!currentJoke) {
        displayError('No joke to copy. Generate one first!');
        return;
    }

    let jokeText = '';

    if (currentJoke.type === 'single') {
        jokeText = currentJoke.joke;
    } else if (currentJoke.type === 'twopart') {
        jokeText = `${currentJoke.setup}\n\n${currentJoke.delivery}`;
    }

    // Copy to clipboard
    navigator.clipboard.writeText(jokeText).then(() => {
        displaySuccess('Joke copied to clipboard! 📋');
    }).catch(err => {
        displayError('Failed to copy joke');
        console.error('Copy error:', err);
    });
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get initial joke on load
    getJoke();

    // Add Enter key support for category selection
    document.getElementById('category').addEventListener('change', function() {
        getJoke();
    });

    // Add keyboard shortcut (Space to get new joke)
    document.addEventListener('keydown', function(event) {
        if (event.code === 'Space' && event.target.tagName !== 'INPUT') {
            event.preventDefault();
            getJoke();
        }
    });
});

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { getJoke, displayJoke, copyJoke };
}
