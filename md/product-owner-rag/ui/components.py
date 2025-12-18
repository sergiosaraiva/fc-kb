"""
UI Components and JavaScript for Product Owner RAG Application.

Contains JavaScript code for:
- Keyboard shortcuts (Ctrl+K, /, Escape)
- localStorage management for search history
- Learning path progress tracking
- Bookmarks management
- Quiz performance tracking
"""

# =============================================================================
# KEYBOARD SHORTCUTS AND LOCALSTORAGE JAVASCRIPT
# =============================================================================

KEYBOARD_SHORTCUTS_JS = """
<script>
// Search History localStorage functions
const HISTORY_KEY = 'fc_search_history';
const PROGRESS_KEY = 'fc_learning_progress';
const MAX_HISTORY = 10;

function getSearchHistory() {
    try {
        const history = localStorage.getItem(HISTORY_KEY);
        return history ? JSON.parse(history) : [];
    } catch (e) {
        return [];
    }
}

function saveToHistory(query) {
    if (!query || query.trim() === '') return;
    try {
        let history = getSearchHistory();
        history = history.filter(q => q.toLowerCase() !== query.toLowerCase());
        history.unshift(query);
        history = history.slice(0, MAX_HISTORY);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (e) {
        console.error('Failed to save search history:', e);
    }
}

function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
}

// Learning Path Progress functions
function getLearningProgress() {
    try {
        const progress = localStorage.getItem(PROGRESS_KEY);
        return progress ? JSON.parse(progress) : {};
    } catch (e) {
        return {};
    }
}

function markTopicComplete(pathId, topicId) {
    try {
        let progress = getLearningProgress();
        if (!progress[pathId]) {
            progress[pathId] = [];
        }
        if (!progress[pathId].includes(topicId)) {
            progress[pathId].push(topicId);
        }
        localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));
        return progress;
    } catch (e) {
        console.error('Failed to save progress:', e);
        return {};
    }
}

function isTopicComplete(pathId, topicId) {
    const progress = getLearningProgress();
    return progress[pathId] && progress[pathId].includes(topicId);
}

function getPathProgress(pathId, totalTopics) {
    const progress = getLearningProgress();
    const completed = progress[pathId] ? progress[pathId].length : 0;
    return {
        completed: completed,
        total: totalTopics,
        percentage: totalTopics > 0 ? Math.round((completed / totalTopics) * 100) : 0
    };
}

function clearProgress() {
    localStorage.removeItem(PROGRESS_KEY);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && !e.target.matches('input, textarea'))) {
        e.preventDefault();
        const searchInput = document.querySelector('input[data-testid="stTextInput"]') ||
                           document.querySelector('input[type="text"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    if (e.key === 'Escape') {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.matches('input, textarea')) {
            activeElement.blur();
        }
    }
});

// Bookmarks functions
const BOOKMARKS_KEY = 'fc_bookmarks';

function getBookmarks() {
    try {
        const bookmarks = localStorage.getItem(BOOKMARKS_KEY);
        return bookmarks ? JSON.parse(bookmarks) : [];
    } catch (e) {
        return [];
    }
}

function addBookmark(question, answer, timestamp) {
    try {
        let bookmarks = getBookmarks();
        // Check if already bookmarked
        if (!bookmarks.find(b => b.question === question)) {
            bookmarks.unshift({ question, answer, timestamp, id: Date.now() });
            bookmarks = bookmarks.slice(0, 20); // Keep max 20 bookmarks
            localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
        }
        return bookmarks;
    } catch (e) {
        console.error('Failed to save bookmark:', e);
        return [];
    }
}

function removeBookmark(id) {
    try {
        let bookmarks = getBookmarks();
        bookmarks = bookmarks.filter(b => b.id !== id);
        localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
        return bookmarks;
    } catch (e) {
        return [];
    }
}

function isBookmarked(question) {
    const bookmarks = getBookmarks();
    return bookmarks.some(b => b.question === question);
}

function clearBookmarks() {
    localStorage.removeItem(BOOKMARKS_KEY);
}

// Quiz Performance Tracking (for adaptive learning)
const QUIZ_PERFORMANCE_KEY = 'fc_quiz_performance';

function getQuizPerformance() {
    try {
        const perf = localStorage.getItem(QUIZ_PERFORMANCE_KEY);
        return perf ? JSON.parse(perf) : { totalQuizzes: 0, totalCorrect: 0, totalQuestions: 0, topicScores: {} };
    } catch (e) {
        return { totalQuizzes: 0, totalCorrect: 0, totalQuestions: 0, topicScores: {} };
    }
}

function saveQuizResult(score, total, topic) {
    try {
        let perf = getQuizPerformance();
        perf.totalQuizzes += 1;
        perf.totalCorrect += score;
        perf.totalQuestions += total;
        if (topic) {
            if (!perf.topicScores[topic]) {
                perf.topicScores[topic] = { correct: 0, total: 0 };
            }
            perf.topicScores[topic].correct += score;
            perf.topicScores[topic].total += total;
        }
        localStorage.setItem(QUIZ_PERFORMANCE_KEY, JSON.stringify(perf));
        return perf;
    } catch (e) {
        return {};
    }
}

function getQuizDifficulty() {
    const perf = getQuizPerformance();
    if (perf.totalQuestions < 5) return 'medium'; // Not enough data
    const accuracy = perf.totalCorrect / perf.totalQuestions;
    if (accuracy >= 0.8) return 'hard';
    if (accuracy <= 0.4) return 'easy';
    return 'medium';
}

function clearQuizPerformance() {
    localStorage.removeItem(QUIZ_PERFORMANCE_KEY);
}

// Make functions available globally
window.fcSearchHistory = {
    get: getSearchHistory,
    save: saveToHistory,
    clear: clearHistory
};
window.fcLearningProgress = {
    get: getLearningProgress,
    mark: markTopicComplete,
    isComplete: isTopicComplete,
    getPath: getPathProgress,
    clear: clearProgress
};
window.fcBookmarks = {
    get: getBookmarks,
    add: addBookmark,
    remove: removeBookmark,
    isBookmarked: isBookmarked,
    clear: clearBookmarks
};
window.fcQuizPerformance = {
    get: getQuizPerformance,
    save: saveQuizResult,
    getDifficulty: getQuizDifficulty,
    clear: clearQuizPerformance
};
</script>
"""
