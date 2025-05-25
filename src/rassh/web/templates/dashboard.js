// RASSH Honeypot Dashboard JavaScript
class RasshDashboard {
    constructor() {
        this.socket = io();
        this.lastFaceUpdate = Date.now();
        this.setupEventListeners();
        this.startPeriodicUpdates();
        this.initializeAnimations();
    }

    setupEventListeners() {
        // WebSocket events
        this.socket.on('connect', () => {
            console.log('Connected to honeypot');
            this.updateStatus('online');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from honeypot');
            this.updateStatus('offline');
        });

        this.socket.on('face_update', (data) => {
            this.updateFace(data.face, data.mood, data.event);
        });

        this.socket.on('activity_update', (data) => {
            this.addActivityItem(data);
        });
    }

    updateStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = statusDot.nextElementSibling;
        
        if (status === 'online') {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Online';
        } else {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Offline';
        }
    }

    updateFace(face, mood, event = null) {
        const faceElement = document.getElementById('face');
        const moodElement = document.getElementById('moodText');
        const lastActivityElement = document.getElementById('lastActivity');

        // Animate face change
        faceElement.style.transform = 'scale(0.8)';
        setTimeout(() => {
            faceElement.textContent = face;
            faceElement.style.transform = 'scale(1)';
            
            // Add bounce animation
            faceElement.style.animation = 'none';
            setTimeout(() => {
                faceElement.style.animation = 'faceBounce 0.5s ease';
            }, 10);
        }, 150);

        // Update mood text
        moodElement.textContent = this.getMoodDescription(mood);
        
        // Update last activity
        lastActivityElement.textContent = `Last activity: ${new Date().toLocaleTimeString()}`;

        // Add special effects for certain events
        if (event) {
            this.triggerEventEffect(event, mood);
        }

        this.lastFaceUpdate = Date.now();
    }

    getMoodDescription(mood) {
        const descriptions = {
            'excited': 'Excited - New visitor detected!',
            'happy': 'Happy - Someone\'s trying to log in!',
            'laughing': 'Laughing - This attacker is persistent!',
            'mischievous': 'Mischievous - Time to mess with them...',
            'alert': 'Alert - Monitoring for threats',
            'focused': 'Focused - Analyzing commands',
            'suspicious': 'Suspicious - Something\'s not right...',
            'sleeping': 'Sleeping - No activity for a while',
            'drowsy': 'Drowsy - Getting quiet around here',
            'bored': 'Bored - Waiting for some action',
            'angry': 'Angry - Under heavy attack!',
            'annoyed': 'Annoyed - These attacks are getting old',
            'protective': 'Protective - Blocking malicious activity',
            'thinking': 'Thinking - Processing information',
            'confused': 'Confused - Something unexpected happened',
            'smug': 'Smug - Successfully fooled an attacker!'
        };
        return descriptions[mood] || 'Unknown mood';
    }

    triggerEventEffect(event, mood) {
        const container = document.querySelector('.face-container');
        
        // Remove existing effect classes
        container.classList.remove('effect-excited', 'effect-alert', 'effect-angry');
        
        // Add appropriate effect
        if (['excited', 'happy', 'laughing'].includes(mood)) {
            container.classList.add('effect-excited');
        } else if (['alert', 'suspicious', 'protective'].includes(mood)) {
            container.classList.add('effect-alert');
        } else if (['angry', 'annoyed'].includes(mood)) {
            container.classList.add('effect-angry');
        }

        // Remove effect after animation
        setTimeout(() => {
            container.classList.remove('effect-excited', 'effect-alert', 'effect-angry');
        }, 1000);
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.stats) {
                document.getElementById('totalSessions').textContent = data.stats.total_sessions;
                document.getElementById('activeSessions').textContent = data.stats.active_sessions;
                document.getElementById('commandsToday').textContent = data.stats.recent_commands;
                document.getElementById('totalCommands').textContent = data.stats.total_commands;
                
                // Update top IPs
                this.updateTopIPs(data.stats.top_ips);
            }

            // Update face if provided
            if (data.face && data.mood) {
                this.updateFace(data.face, data.mood);
            }
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    async updateActivity() {
        try {
            const response = await fetch('/api/recent_activity');
            const activities = await response.json();
            
            const feedElement = document.getElementById('activityFeed');
            feedElement.innerHTML = '';
            
            if (activities.length === 0) {
                feedElement.innerHTML = '<div class="activity-item"><span class="activity-time">No recent activity</span></div>';
                return;
            }

            activities.forEach(activity => {
                this.addActivityItem(activity, false);
            });
        } catch (error) {
            console.error('Failed to update activity:', error);
        }
    }

    addActivityItem(activity, animate = true) {
        const feedElement = document.getElementById('activityFeed');
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        
        const time = new Date(activity.timestamp).toLocaleTimeString();
        const actionColor = this.getActionColor(activity.action);
        
        activityItem.innerHTML = `
            <div class="activity-time">${time}</div>
            <div><strong>${activity.client_ip}</strong> executed: <span class="activity-command">${activity.command}</span></div>
            <div>Action: <span class="activity-action" style="color: ${actionColor}">${activity.action}</span> (Reward: ${activity.reward})</div>
        `;

        if (animate) {
            activityItem.style.opacity = '0';
            activityItem.style.transform = 'translateX(-20px)';
        }

        feedElement.insertBefore(activityItem, feedElement.firstChild);

        if (animate) {
            setTimeout(() => {
                activityItem.style.opacity = '1';
                activityItem.style.transform = 'translateX(0)';
                activityItem.style.transition = 'all 0.3s ease';
            }, 10);
        }

        // Keep only last 20 items
        while (feedElement.children.length > 20) {
            feedElement.removeChild(feedElement.lastChild);
        }
    }

    getActionColor(action) {
        const colors = {
            'ALLOW': '#00ff00',
            'DELAY': '#ffff00',
            'FAKE': '#ff6600',
            'INSULT': '#ff0066',
            'BLOCK': '#ff0000'
        };
        return colors[action] || '#ffffff';
    }

    updateTopIPs(ips) {
        const ipListElement = document.getElementById('ipList');
        ipListElement.innerHTML = '';
        
        if (!ips || ips.length === 0) {
            ipListElement.innerHTML = '<div class="ip-item">No data yet</div>';
            return;
        }

        ips.forEach((ip, index) => {
            const ipItem = document.createElement('div');
            ipItem.className = 'ip-item';
            ipItem.textContent = `${index + 1}. ${ip}`;
            ipListElement.appendChild(ipItem);
        });
    }

    startPeriodicUpdates() {
        // Update stats every 5 seconds
        setInterval(() => this.updateStats(), 5000);
        
        // Update activity every 10 seconds
        setInterval(() => this.updateActivity(), 10000);
        
        // Initial updates
        this.updateStats();
        this.updateActivity();
    }

    initializeAnimations() {
        // Add CSS for special effects
        const style = document.createElement('style');
        style.textContent = `
            .effect-excited {
                animation: excitedPulse 1s ease-in-out;
            }
            
            .effect-alert {
                animation: alertFlash 0.5s ease-in-out;
            }
            
            .effect-angry {
                animation: angryShake 0.5s ease-in-out;
            }
            
            @keyframes excitedPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); box-shadow: 0 0 30px rgba(0, 255, 0, 0.5); }
            }
            
            @keyframes alertFlash {
                0%, 100% { border-color: #00ff00; }
                50% { border-color: #ffff00; box-shadow: 0 0 20px rgba(255, 255, 0, 0.5); }
            }
            
            @keyframes angryShake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new RasshDashboard();
});