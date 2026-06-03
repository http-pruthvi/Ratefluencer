/**
 * Ratefluencer AI — Client Application Logic
 * Implements single-page application routing, live API integrations, and Chart.js dashboards.
 */

// Global Chart Instances mapping
const chartInstances = {};

// Helper to handle navigation between sections
function navigateTo(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show target page
    const targetPage = document.getElementById(`page-${pageId}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    const activeLink = document.getElementById(`nav-${pageId}`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Handle auto-loading on page transition
    if (pageId === 'trends') {
        loadTrends();
    }
}

// Register click events on navigation links
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.getAttribute('data-page');
            navigateTo(pageId);
        });
    });
});

/**
 * ─── CHART HELPERS ──────────────────────────────────────────────────────────
 */

// Render a circular gauge indicator for performance indicators
function renderGauge(canvasId, value, colorHex) {
    // If instance exists, destroy it to prevent hover issues
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
        delete chartInstances[canvasId];
    }

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [colorHex, 'rgba(255, 255, 255, 0.05)'],
                borderWidth: 0
            }]
        },
        options: {
            rotation: 270,          // Semicircle start at bottom
            circumference: 180,     // Half circle
            cutout: '80%',          // Slender donut thickness
            aspectRatio: 1.5,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            layout: {
                padding: { bottom: 10 }
            }
        },
        plugins: [{
            id: 'gaugeCenterText',
            afterDraw(chart) {
                const { ctx, chartArea: { left, right, bottom } } = chart;
                ctx.save();
                const centerX = (left + right) / 2;
                const centerY = bottom - 5;
                
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                
                // Score Value
                ctx.font = '800 1.8rem Outfit, sans-serif';
                ctx.fillStyle = '#ffffff';
                ctx.fillText(Math.round(value), centerX, centerY);
                
                // Scale Label
                ctx.font = '600 0.8rem Inter, sans-serif';
                ctx.fillStyle = '#94a3b8';
                ctx.fillText(' / 100', centerX + 30, centerY - 2);
                ctx.restore();
            }
        }]
    });
}

// Render historical and forecasted line graphs
function renderGrowthChart(historical, predicted) {
    const canvasId = 'growth-chart';
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
        delete chartInstances[canvasId];
    }

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const labels = [];
    const historicalData = [];
    const predictedData = [];

    // Generate indices
    for (let i = 0; i < historical.length; i++) {
        labels.push(`D-${historical.length - 1 - i}`);
        historicalData.push(historical[i]);
        predictedData.push(null);
    }

    // Connect the prediction trace to the final historical index
    predictedData[historical.length - 1] = historical[historical.length - 1];

    for (let i = 0; i < predicted.length; i++) {
        labels.push(`D+${i + 1}`);
        historicalData.push(null);
        predictedData.push(predicted[i]);
    }

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Historical Followers',
                    data: historicalData,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.04)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 3,
                    pointRadius: 2,
                    pointBackgroundColor: '#818cf8',
                    spanGaps: true
                },
                {
                    label: '30-Day Forecast',
                    data: predictedData,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.02)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 3,
                    borderDash: [6, 6],
                    pointRadius: 0,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter, sans-serif', size: 11 }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.02)' },
                    ticks: {
                        color: '#64748b',
                        maxTicksLimit: 10,
                        font: { size: 10 }
                    }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.02)' },
                    ticks: {
                        color: '#64748b',
                        font: { size: 10 },
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}


/**
 * ─── TRACK 1: CREATOR PROFILE ANALYZER ───────────────────────────────────────
 */

async function runInfluencerAudit() {
    const usernameInput = document.getElementById('scorer-input').value.trim();
    if (!usernameInput) return;

    // Show Loading
    document.getElementById('scorer-loading').style.display = 'block';
    document.getElementById('scorer-results').style.display = 'none';
    document.getElementById('scorer-error').style.display = 'none';

    try {
        const username = usernameInput.startsWith('@') ? usernameInput.substring(1) : usernameInput;
        const response = await fetch(`/api/influencer/${encodeURIComponent(username)}`);
        
        if (!response.ok) {
            throw new Error(`Server returned status code: ${response.status}`);
        }
        
        const payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || "Profile scoring failed.");
        }

        const data = payload.data;

        // Render Gauges
        renderGauge('gauge-auth', data.authenticity_score, 'var(--indigo)');
        renderGauge('gauge-growth', data.growth_score, 'var(--emerald)');
        renderGauge('gauge-brand', data.growth_rate_30d_pct > 0 ? 80 : 40, 'var(--cyan)'); // fallback match score representation
        renderGauge('gauge-rate', data.ratefluencer_score, 'var(--rose)');

        // Populate Profile Card
        const profile = data.profile;
        document.getElementById('profile-card').innerHTML = `
            <div class="profile-username">@${profile.username}</div>
            <div class="profile-meta">${profile.platform} • ${profile.content_category.toUpperCase()}</div>
            <div class="profile-bio">${profile.bio || "No biography details available."}</div>
        `;

        // Populate Metrics Table
        document.getElementById('metrics-table').innerHTML = `
            <div class="metrics-row">
                <span class="metrics-key">Followers</span>
                <span class="metrics-val">${profile.followers.toLocaleString()}</span>
            </div>
            <div class="metrics-row">
                <span class="metrics-key">Following</span>
                <span class="metrics-val">${profile.following.toLocaleString()}</span>
            </div>
            <div class="metrics-row">
                <span class="metrics-key">Posts Count</span>
                <span class="metrics-val">${profile.posts_count.toLocaleString()}</span>
            </div>
            <div class="metrics-row">
                <span class="metrics-key">Engagement Rate</span>
                <span class="metrics-val">${(profile.engagement_rate * 100).toFixed(2)}%</span>
            </div>
            <div class="metrics-row">
                <span class="metrics-key">Avg Likes</span>
                <span class="metrics-val">${Math.round(profile.avg_likes).toLocaleString()}</span>
            </div>
            <div class="metrics-row">
                <span class="metrics-key">Avg Comments</span>
                <span class="metrics-val">${Math.round(profile.avg_comments).toLocaleString()}</span>
            </div>
        `;

        // Populate Growth Timeline
        renderGrowthChart(data.historical_history, data.predicted_history);
        
        const sign = data.growth_rate_30d_pct >= 0 ? '+' : '';
        document.getElementById('growth-rate-text').innerText = 
            `Projected 30-Day Follower Change: ${sign}${data.growth_rate_30d_pct.toFixed(2)}%`;

        // Load Semantic Brand Matches
        await loadBrandMatches(profile.id);

        // Transition views
        document.getElementById('scorer-loading').style.display = 'none';
        document.getElementById('scorer-results').style.display = 'block';

    } catch (err) {
        document.getElementById('scorer-loading').style.display = 'none';
        const errDiv = document.getElementById('scorer-error');
        errDiv.innerText = `Error: ${err.message}`;
        errDiv.style.display = 'block';
    }
}

// Fetch semantic brand matches for audited creator ID
async function loadBrandMatches(creatorId) {
    const grid = document.getElementById('brands-grid');
    grid.innerHTML = '<p class="page-desc">Retrieving vector campaigns...</p>';

    try {
        const response = await fetch(`/api/influencer/${creatorId}/brand-matches`);
        const payload = await response.json();
        
        if (!payload.success) {
            grid.innerHTML = '<p class="page-desc" style="color:var(--rose);">Failed to retrieve brand alignments.</p>';
            return;
        }

        const brands = payload.data;
        if (!brands || brands.length === 0) {
            grid.innerHTML = '<p class="page-desc">No semantic brand matches discovered.</p>';
            return;
        }

        grid.innerHTML = brands.map(brand => `
            <div class="glass-card brand-card">
                <div>
                    <span class="brand-industry">${brand.industry}</span>
                    <p class="brand-name" style="margin-top:8px;">${brand.name}</p>
                    <p class="brand-desc">${brand.description}</p>
                </div>
                <div class="brand-score-row">
                    <span class="brand-score-label">Match Score</span>
                    <span class="brand-score-val">${Math.round(brand.match_score)}%</span>
                </div>
            </div>
        `).join('');

    } catch (err) {
        grid.innerHTML = `<p class="page-desc" style="color:var(--rose);">Error loading brands: ${err.message}</p>`;
    }
}


/**
 * ─── TRACK 1: SEMANTIC CAMPAIGN MATCHER ──────────────────────────────────────
 */

async function searchCreators() {
    const brief = document.getElementById('matcher-input').value.trim();
    if (!brief) return;

    document.getElementById('matcher-loading').style.display = 'block';
    document.getElementById('matcher-results').style.display = 'none';
    document.getElementById('matcher-error').style.display = 'none';

    try {
        const response = await fetch('/api/influencer/search-by-brief', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brief })
        });

        const payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || "Brief search query failed.");
        }

        const listDiv = document.getElementById('matcher-list');
        const creators = payload.data;

        if (!creators || creators.length === 0) {
            listDiv.innerHTML = '<p class="page-desc">No ideal creator partners matched this campaign description.</p>';
        } else {
            listDiv.innerHTML = creators.map(creator => `
                <div class="glass-card creator-row">
                    <div class="creator-info">
                        <span class="creator-username">@${creator.username}</span>
                        <span class="creator-tag">${creator.content_category}</span>
                        <p class="creator-meta">Platform: ${creator.platform} | Followers: ${creator.followers.toLocaleString()}</p>
                        <p class="creator-bio">${creator.bio || "No biography bio available."}</p>
                    </div>
                    <div class="creator-score">
                        <span class="creator-score-label">Semantic Match</span>
                        <p class="creator-score-value">${Math.round(creator.match_score)}%</p>
                    </div>
                </div>
            `).join('');
        }

        document.getElementById('matcher-loading').style.display = 'none';
        document.getElementById('matcher-results').style.display = 'block';

    } catch (err) {
        document.getElementById('matcher-loading').style.display = 'none';
        const errDiv = document.getElementById('matcher-error');
        errDiv.innerText = `Error: ${err.message}`;
        errDiv.style.display = 'block';
    }
}


/**
 * ─── TRACK 2: LIVE TREND DISCOVERY ───────────────────────────────────────────
 */

async function loadTrends() {
    document.getElementById('trends-loading').style.display = 'block';
    document.getElementById('trends-results').style.display = 'none';
    document.getElementById('trends-error').style.display = 'none';

    try {
        const response = await fetch('/api/trends?limit=10');
        const payload = await response.json();
        
        if (!payload.success) {
            throw new Error(payload.error || "Trend lookup failed.");
        }

        const listDiv = document.getElementById('trends-list');
        const trends = payload.data;

        if (!trends || trends.length === 0) {
            listDiv.innerHTML = '<p class="page-desc" style="padding:16px;">No hot topics found at this hour.</p>';
        } else {
            listDiv.innerHTML = trends.map((trend, idx) => `
                <div class="trend-row">
                    <span class="trend-rank">#${idx + 1}</span>
                    <span class="trend-source-tag">${trend.source}</span>
                    <div class="trend-title-container">
                        <div class="trend-title">${trend.topic}</div>
                        <div class="trend-meta">${trend.title}</div>
                    </div>
                    <div class="trend-score-bar">
                        <span class="trend-score-val">${trend.trend_score.toFixed(1)}</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${trend.trend_score}%"></div>
                        </div>
                    </div>
                    <div>
                        <button class="btn-primary btn-sm" onclick="useTrendTopic('${trend.topic.replace(/'/g, "\\'")}', '${trend.source}')">Use Topic</button>
                    </div>
                </div>
            `).join('');
        }

        document.getElementById('trends-loading').style.display = 'none';
        document.getElementById('trends-results').style.display = 'block';

    } catch (err) {
        document.getElementById('trends-loading').style.display = 'none';
        const errDiv = document.getElementById('trends-error');
        errDiv.innerText = `Error: ${err.message}`;
        errDiv.style.display = 'block';
    }
}

// Redirect trend topic to the Content Studio with pre-filled inputs
function useTrendTopic(topic, source) {
    document.getElementById('studio-topic').value = topic;
    
    // Choose appropriate selection option
    const categorySelect = document.getElementById('studio-category');
    let matchedOption = 'tech';
    
    const lowerTopic = topic.toLowerCase();
    if (lowerTopic.includes('fit') || lowerTopic.includes('workout') || lowerTopic.includes('cardi')) {
        matchedOption = 'fitness';
    } else if (lowerTopic.includes('finance') || lowerTopic.includes('invest') || lowerTopic.includes('money')) {
        matchedOption = 'finance';
    } else if (lowerTopic.includes('food') || lowerTopic.includes('recipe')) {
        matchedOption = 'food';
    } else if (lowerTopic.includes('travel')) {
        matchedOption = 'travel';
    } else if (lowerTopic.includes('game') || lowerTopic.includes('playstation') || lowerTopic.includes('xbox')) {
        matchedOption = 'gaming';
    } else if (lowerTopic.includes('fashion') || lowerTopic.includes('wear')) {
        matchedOption = 'fashion';
    }
    
    categorySelect.value = matchedOption;
    navigateTo('studio');
}


/**
 * ─── TRACK 2: AI CAMPAIGN CONTENT STUDIO ──────────────────────────────────────
 */

// Regex/String parser to segment [HOOK], [STORY], [INSIGHTS], [CTA]
function parseScriptText(script) {
    const parsed = { hook: '', story: '', insights: '', cta: '' };
    
    const hookMatch = script.match(/\[HOOK\]([\s\S]*?)(?=\[STORY\]|$)/i);
    const storyMatch = script.match(/\[STORY\]([\s\S]*?)(?=\[INSIGHTS\]|$)/i);
    const insightsMatch = script.match(/\[INSIGHTS\]([\s\S]*?)(?=\[CTA\]|$)/i);
    const ctaMatch = script.match(/\[CTA\]([\s\S]*?)$/i);
    
    if (hookMatch) parsed.hook = hookMatch[1].trim();
    if (storyMatch) parsed.story = storyMatch[1].trim();
    if (insightsMatch) parsed.insights = insightsMatch[1].trim();
    if (ctaMatch) parsed.cta = ctaMatch[1].trim();

    // Fallback if parsing fails to locate headers
    if (!parsed.hook && !parsed.story && !parsed.insights && !parsed.cta) {
        parsed.story = script;
    }

    return parsed;
}

// Executes LangGraph node workflow
async function runAgentPipeline() {
    const topic = document.getElementById('studio-topic').value.trim();
    const category = document.getElementById('studio-category').value;
    if (!topic) return;

    document.getElementById('studio-loading').style.display = 'block';
    document.getElementById('studio-results').style.display = 'none';
    document.getElementById('studio-error').style.display = 'none';

    try {
        const response = await fetch('/api/content/agent-pipeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, category })
        });

        const payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || "Agent execution failed.");
        }

        const data = payload.data;

        // Parse Script sections
        const scriptData = parseScriptText(data.script);
        document.getElementById('script-bands').innerHTML = `
            ${scriptData.hook ? `
                <div class="script-band band-hook">
                    <span class="band-label">🎬 Hook (0-5s)</span>
                    <p>${scriptData.hook.replace(/\n/g, '<br>')}</p>
                </div>
            ` : ''}
            ${scriptData.story ? `
                <div class="script-band band-story">
                    <span class="band-label">📖 Story (5-25s)</span>
                    <p>${scriptData.story.replace(/\n/g, '<br>')}</p>
                </div>
            ` : ''}
            ${scriptData.insights ? `
                <div class="script-band band-insights">
                    <span class="band-label">💡 Key Insights (25-50s)</span>
                    <p>${scriptData.insights.replace(/\n/g, '<br>')}</p>
                </div>
            ` : ''}
            ${scriptData.cta ? `
                <div class="script-band band-cta">
                    <span class="band-label">⚡ Call To Action (50-60s)</span>
                    <p>${scriptData.cta.replace(/\n/g, '<br>')}</p>
                </div>
            ` : ''}
        `;

        // Render Social Outputs
        document.getElementById('linkedin-text').innerText = data.linkedin_post;
        document.getElementById('instagram-text').innerText = data.instagram_caption;
        document.getElementById('hashtags-text').innerText = (data.hashtags || []).join(' ');

        // Render virality stats
        renderGauge('gauge-virality', data.virality_score, 'var(--violet)');
        document.getElementById('perf-views').innerText = data.expected_views.toLocaleString();
        document.getElementById('perf-likes').innerText = data.expected_likes.toLocaleString();
        document.getElementById('perf-shares').innerText = data.expected_shares.toLocaleString();

        // Render critiques
        const critiqueDiv = document.getElementById('insights-list');
        if (data.insights && data.insights.length > 0) {
            critiqueDiv.innerHTML = data.insights.map(item => {
                const type = (item.toLowerCase().includes('missing') || item.toLowerCase().includes('long')) ? 'warning' : 'positive';
                const dotClass = type === 'warning' ? 'insight-warning' : 'insight-positive';
                return `
                    <div class="insight-item">
                        <div class="insight-dot ${dotClass}"></div>
                        <p>${item}</p>
                    </div>
                `;
            }).join('');
        } else {
            critiqueDiv.innerHTML = '<p class="page-desc">No structure critiques generated.</p>';
        }

        document.getElementById('studio-loading').style.display = 'none';
        document.getElementById('studio-results').style.display = 'block';

    } catch (err) {
        document.getElementById('studio-loading').style.display = 'none';
        const errDiv = document.getElementById('studio-error');
        errDiv.innerText = `Error: ${err.message}`;
        errDiv.style.display = 'block';
    }
}
