let userStoryName = '';
let selectedOption = 'All';

const statusOptions = new Map([
    [1, 'Not Started'],
    [2, 'In Development'],
    [3, 'Testing'],
    [4, 'Production']
]);

const phases = new Map([
    [1, 'Sprint Planning'],
    [2, 'Daily Scrum'],
    [3, 'Review'],
    [4, 'Retrospective']
]);

const phaseImageUrls = new Map([
    [1, 'sprint-planning'],
    [2, 'daily-scrum'],
    [3, 'review'],
    [4, 'retrospective']
]);

let currentPhaseImgUrl = '';

document.addEventListener('DOMContentLoaded', () => {
    fetchUserStories();
    fetchSprint();

    const backlogList = document.querySelector('#backlog-list');
    if (backlogList) {
        backlogList.addEventListener('click', (e) => {
            if (e.target && e.target.nodeName === 'LI') {
                const current = backlogList.querySelector('.highlighted');
                if (current && current !== e.target) {
                    current.classList.remove('highlighted');
                }

                e.target.classList.toggle('highlighted');
                userStoryName = e.target.textContent || e.target.innerText;

                fetchTeamMembers();
                fetchStoryPoints();
            }
        });
    }

    const filterSprintOption = document.querySelector('.filter_option select');
    if (filterSprintOption) {
        filterSprintOption.addEventListener('change', function () {
            selectedOption = this.options[this.selectedIndex].text;
            fetchUserStories();
        });
    }

    const pushStatusButton = document.querySelector('#push-status');
    if (pushStatusButton) {
        pushStatusButton.addEventListener('click', () => {
            updateStoryStatus('Push');
        });
    }

    const reverseStatusButton = document.querySelector('#reverse-status');
    if (reverseStatusButton) {
        reverseStatusButton.addEventListener('click', () => {
            updateStoryStatus('Reverse');
        });
    }

    const nextPhaseButton = document.querySelector('#next-phase-button');
    if (nextPhaseButton) {
        nextPhaseButton.addEventListener('click', () => {
            updateSprint('Push');
        });
    }

    const reversePhaseButton = document.querySelector('#reverse-phase-button');
    if (reversePhaseButton) {
        reversePhaseButton.addEventListener('click', () => {
            updateSprint('Reverse');
        });
    }
});

async function postForm(endpoint, data = {}) {
    const formData = new FormData();

    Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            formData.append(key, value);
        }
    });

    const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

async function fetchSprint() {
    try {
        const response = await postForm('/api/fetch_sprint');

        if (!response || response.length === 0) {
            document.querySelector('#current-phase-box').innerHTML =
                '<h2>No current sprint found.</h2>';
            return;
        }

        const currentPhase = response[0].phase;
        currentPhaseImgUrl = '';

        phases.forEach((value, key) => {
            if (value === currentPhase) {
                currentPhaseImgUrl = phaseImageUrls.get(key);
            }
        });

        let htmlContent = `<h2>Current phase is ${currentPhase}</h2>`;

        if (currentPhaseImgUrl) {
            htmlContent += `
                <img 
                    src="/static/scrum/${currentPhaseImgUrl}.jpg" 
                    width="500" 
                    height="300" 
                    alt="${currentPhase}"
                >
            `;
        }

        document.querySelector('#current-phase-box').innerHTML = htmlContent;
    } catch (error) {
        console.error('Error fetching sprint:', error);
    }
}

async function getCurrentPhaseHelper() {
    try {
        const response = await postForm('/api/fetch_sprint');
        return response?.[0]?.phase || null;
    } catch (error) {
        console.error('Error fetching current phase:', error);
        return null;
    }
}

async function updateSprint(update) {
    try {
        const currentPhase = await getCurrentPhaseHelper();

        if (!currentPhase) {
            console.error('No current phase found.');
            return;
        }

        let currentPhaseKey = null;
        phases.forEach((value, key) => {
            if (value === currentPhase) {
                currentPhaseKey = key;
            }
        });

        if (!currentPhaseKey) {
            console.error('Could not match current phase.');
            return;
        }

        let newPhase = null;

        if (update === 'Push' && currentPhaseKey < 4) {
            newPhase = phases.get(currentPhaseKey + 1);
        } else if (update === 'Reverse' && currentPhaseKey > 1) {
            newPhase = phases.get(currentPhaseKey - 1);
        } else {
            console.log('Phase change not allowed.');
            return;
        }

        const response = await postForm('/api/update_phase', {
            newPhaseText: newPhase,
            phaseNumberText: 4
        });

        console.log('Update phase response:', response);
        fetchSprint();
    } catch (error) {
        console.error('Error updating phase:', error);
    }
}

async function fetchUserStories() {
    try {
        const requestData = {};

        if (selectedOption !== 'All') {
            requestData.itemText = selectedOption;
        }

        const response = await postForm('/api/fetch_sprint_stories', requestData);

        let htmlContent = '';

        if (!response || response.length === 0) {
            htmlContent = '<li>No stories found</li>';
            document.querySelector('#backlog-list').innerHTML = htmlContent;

            const teamList = document.querySelector('#team-list');
            if (teamList) {
                teamList.innerHTML = '';
            }

            const aboutTable = document.querySelector('.about table');
            if (aboutTable) {
                aboutTable.innerHTML = '';
            }

            return;
        }

        response.forEach((story) => {
            htmlContent += `<li>${story.user_story_name}</li>`;
        });

        document.querySelector('#backlog-list').innerHTML = htmlContent;

        const firstListItem = document.querySelector('#backlog-list li');
        if (firstListItem && firstListItem.textContent !== 'No stories found') {
            firstListItem.click();
        }
    } catch (error) {
        console.error('Error fetching user stories:', error);
    }
}

async function fetchTeamMembers() {
    if (!userStoryName) return;

    try {
        const response = await postForm('/api/fetch_assign_members', {
            itemText: userStoryName
        });

        let htmlContent = '';

        if (!response || response.length === 0) {
            htmlContent = '<li>No team members assigned</li>';
            document.querySelector('#team-list').innerHTML = htmlContent;
            return;
        }

        response.forEach((member) => {
            htmlContent += `<li>${member.employee_name} [${member.role}]</li>`;
        });

        document.querySelector('#team-list').innerHTML = htmlContent;
    } catch (error) {
        console.error('Error fetching team members:', error);
    }
}

async function fetchStoryPoints() {
    if (!userStoryName) return;

    try {
        const response = await postForm('/api/fetch_story_points', {
            itemText: userStoryName
        });

        const storyPointsHeader = document.querySelector('#story-points');
        if (storyPointsHeader) {
            storyPointsHeader.innerHTML = userStoryName;
        }

        const aboutTable = document.querySelector('.about table');
        if (!aboutTable) return;

        if (!response || response.length === 0) {
            aboutTable.innerHTML = '<tr><td>No story data found.</td></tr>';
            return;
        }

        let htmlContent = '<tr><th>Story Points</th><th>Status</th></tr>';
        htmlContent += `
            <tr>
                <td>${response[0].story_points}</td>
                <td>${response[0].status}</td>
            </tr>
        `;

        aboutTable.innerHTML = htmlContent;
    } catch (error) {
        console.error('Error fetching story points:', error);
    }
}

async function getCurrentStatusHelper() {
    if (!userStoryName) {
        return null;
    }

    try {
        const response = await postForm('/api/fetch_story_points', {
            itemText: userStoryName
        });

        return response?.[0]?.status || null;
    } catch (error) {
        console.error('Error fetching current status:', error);
        return null;
    }
}

async function updateStoryStatus(update) {
    if (!userStoryName) {
        console.error('No user story selected.');
        return;
    }

    try {
        const currentStatus = await getCurrentStatusHelper();

        if (!currentStatus) {
            console.error('No current status found.');
            return;
        }

        let currentStatusKey = null;
        statusOptions.forEach((value, key) => {
            if (value === currentStatus) {
                currentStatusKey = key;
            }
        });

        if (!currentStatusKey) {
            console.error('Could not match current status.');
            return;
        }

        let newStatus = null;

        if (update === 'Push' && currentStatusKey < 4) {
            newStatus = statusOptions.get(currentStatusKey + 1);
        } else if (update === 'Reverse' && currentStatusKey > 1) {
            newStatus = statusOptions.get(currentStatusKey - 1);
        } else {
            console.log('Status change not allowed.');
            return;
        }

        const response = await postForm('/api/update_status', {
            newStatusText: newStatus,
            userStoryText: userStoryName
        });

        console.log('Update status response:', response);

        fetchStoryPoints();
        fetchUserStories();
    } catch (error) {
        console.error('Error updating story status:', error);
    }
}