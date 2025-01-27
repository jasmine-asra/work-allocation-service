# Work Allocation Service

This is a web application built with **Flask** (backend) and **React** (frontend) to manage **doables** and their **allocations** to users. Users can be automatically allocated doables in the system based on priority, age and type preference. Doables are allocated either singularly or by case, and allocations can be viewed, filtered, and modified.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
4. [Changes to Models](#changes-to-models)
5. [Assumptions Made](#assumptions-made)

---

## Installation

### Backend Setup (Flask)
1. **Install Python** (if not already installed) from [python.org](https://www.python.org/).
2. **Install the required Python dependencies**. Navigate to the `backend` directory in your terminal and run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask app** by navigating to the `backend` directory and running:
   ```bash
   python app.py
   ```
   This will start the Flask server and the backend should be accessible at `http://localhost:5000`.

### Frontend Setup (React)
1. **Install Node.js** (if not already installed) from [nodejs.org](https://nodejs.org/).
   
2. **Install the required npm packages**. Navigate to the `frontend` directory and run:
   ```bash
   npm install
   ```

3. **Start the React app** by running:
   ```bash
   npm start
   ```
   This will start the React development server and the frontend should be accessible at `http://localhost:3000`.

---

## Usage

Once both the backend and frontend are running, you can:

1. **Add a Doable**: 
   - Click the "Add Doable" button in the header. This will allow you to add a new doable to the system.
   
2. **Users View**: 
   - From the home page, you can view all the users in the system and see which doables they have been allocated by expanding a user card. Doables that are not marked as complete will be listed.
   - You can allocate a **single doable** to a user which assigns the oldest, highest priority doable that matches their preference. 
   - You can also **allocate all doables of a case** to a user. The system will automatically assign an entire case-load of doables to a user by finding the case which has no associated doables currently allocated, and which has the oldest, highest priority doable that matches the user's preference associated with it.
   - You can assign a user all **unallocated doables** associated with a doable they have already been allocated. This does not reallocate any already allocated doables to avoid confusion.

3. **Filter Users**: 
   - You can filter users by **name** or **preferred type** to make it easier to find the user you want to allocate doables to.

4. **Allocations View**: 
   - Click the "Allocations" button in the header to go to the allocations view. This page shows all allocations in the order in which they should be tackled.
   - You can **toggle the view** to show single allocations or group them by **case ID**.
   - Each allocation card shows metadata, including the user assigned to the doable, the doable’s title, date created and status.
   - A **"case" badge** will indicate if the allocation was made via case allocation.
   - You can unallocate a **single doable** or unallocate all doables associated with the **case**.
   - You can **mark a doable as complete** by clicking the tick in the top right corner. Once marked complete, the doable status is updated to **"completed"** and the options to unallocate disappear.

5. **Search Allocations**: 
   - Use the search bar to filter allocations by **doable title**, **type**, or **status**.

---

## Changes to Models

### User Model Changes
I made the following changes to the **User** model:
- Added `first_name` and `last_name` fields to capture the full name of users.
- Added an `id` field to ensure each user can be uniquely identified.

These changes were made to allow for a more robust and user-friendly management system.

### Doable Model Changes
I made the following changes to the **Doable** model:
- Added a `priority` field to indicate whether the doable is "high", "medium" or "low" priority.
- Added a `status` field to track the current status of a doable ("pending", "allocated", "completed"). The `status` field tracks the lifecycle of a doable and controls its allocation process.

### Allocation Model (Junction Table)
I created an **Allocation** model to act as a junction table between **users** and **doables**. This model stores the allocation details, including the `doable_id`, `user_id`, and the allocation-specific data `allocated_at` and `is_case_allocation`.

I opted to create a separate **Allocation** model instead of adding a `user_id` field directly to the **Doable** model for the following reasons:
- A dedicated model allows easy tracking of allocation type (single or case-based).
- Adding a separate model enables better handling of future changes, such as supporting multiple users per doable.
- Seperating the concerns helps to maintain cleaner, more maintainable code.

---

## Assumptions Made

1. **Service Requirements**: 
   - The task was to create a service that provides a full view of **users** and **allocations** for a manager, rather than for individual users to track their own **doables**.

2. **Human-Readable Doable IDs**: 
   - I assumed that **Doable IDs** need to be human-readable, so I manually generate them rather than using **UUIDs**.

3. **User Identification**:  
   - In the original model, the `user_name` field was used to store a combination of the user’s first name and their preferred doable type (e.g., `emma.emails`). While this could serve as a unique identifier, I felt that it was not as **scalable** or **robust** for uniquely identifying users, especially as the system grows.
   - To address this, I opted to use **UUIDs** as unique identifiers for users, ensuring a more **future-proof** and reliable identification system. However, I retained the `user_name` field as it was part of the original task, and it could still serve as a descriptive label or display value in the user interface.

4. **Task-Doables Are Always Associated with a Case**:
   - I assumed that **task-type doables** are always associated with a **case**. Therefore, these doables require a case ID to be created.

5. **Single Doables Are Only Assigned to Matching Users**:
   - When assigning cases, doables of any type can be assigned to users with any preference. However, the task specifies that when allocating a single doable users should be assigned the highest priority doable that they "can do", so I assumed that they *cannot do* single doables that do not match their preference.

6. **Doables Persist After Completion**: 
   - Doables should remain in storage after being completed. The system retains all doables, even those marked as complete, to maintain historical data.

7. **Case Allocation Restrictions**: 
   - Cases with associated doables that have already been assigned to a user cannot be automatically reassigned. The system allocates the next available case with no allocated doables. This prevents a doable being reassigned after a user has already begun to complete it. 
   - This restriction would not be necessary if users could manage their own doables by, for example, marking them as `in_progress` as this would allow doables which had not been started to be reassigned.

8. **Case ID for "message_457"**: 
   - The case ID for **message_457 ("case_setup_2")** is an exception as it does not follow the same pattern as the other doables.