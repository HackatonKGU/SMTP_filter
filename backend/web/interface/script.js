document.addEventListener('DOMContentLoaded', () => {
    const serverStatus = document.getElementById('server-status');
    const dbStatus = document.getElementById('db-status');

    function updateStatus(element, status, text) {
        element.className = 'status-indicator ' + status;
        element.textContent = text;
    }

    async function checkStatus() {
        try {
            const response = await fetch('/health');
            if (response.ok) {
                const data = await response.json();

                if (data.database === 'ok') {
                    updateStatus(dbStatus, 'ok', 'Работает');
                } else {
                    updateStatus(dbStatus, 'error', 'Ошибка');
                }

                updateStatus(serverStatus, 'ok', 'Работает');
            } else {
                updateStatus(serverStatus, 'error', 'Ошибка');
                updateStatus(dbStatus, 'error', 'Неизвестно');
            }
        } catch (error) {
            updateStatus(serverStatus, 'error', 'Ошибка');
            updateStatus(dbStatus, 'error', 'Неизвестно');
        }
    }

    checkStatus();
    setInterval(checkStatus, 15000); // Проверка каждые 15 секунд
});