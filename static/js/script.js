document.addEventListener('DOMContentLoaded', function() {
    var userList = document.querySelector('.user-list');

    // Function to fetch users from Flask endpoint
    function fetchUsers() {
        fetch('/get_users')
            .then(response => response.json())
            .then(data => {
                // Clear existing list items
                userList.innerHTML = '';

                // Iterate through received data and create list items
                data.forEach(user => {
                    var listItem = document.createElement('li');
                    listItem.textContent = `${user.name} - ${user.email}`;
                    userList.appendChild(listItem);
                });
            })
            .catch(error => {
                console.error('Error fetching users:', error);
            });
    }

    // Initial fetch when the page loads
    fetchUsers();

    // Optional: Periodically update the user list (example: every 30 seconds)
    setInterval(fetchUsers, 30000); // Adjust the interval as needed
});
