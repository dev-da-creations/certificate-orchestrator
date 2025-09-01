# Certificate Orchestrator

The Certificate Orchestrator project aims to automate and streamline the certification process within an organisation. It is being developed incrementally to validate planned objectives and gradually evolve into a more efficient and effective IT product.

# 🔧 Prerequisites

Before running the scripts, please ensure the following:

  - Database Setup

Create a database instance. The project currently uses SQL Server Management Studio (SSMS).
PostgreSQL support will be added in the future.

  - Sample Data

Use the data from the Inserting_Values_To_CML_Table.sql script.
Ensure that field names in the database match the script definitions.

  - Environment Variables

Create a .env file in the ../scripts directory.
Store your Gmail App Password under the variable name Password.
(Future enhancement: explore alternative SMTP providers for sending emails.)

# 🎯 Current Vision & Use Case

The project’s current goal is to send automated alerts to certificate owners when certificates are:

  - Expiring today
  - Expiring in 7, 14, or 30 days
  - Expired within the last 7, 14, or 30 days

Email Behavior

  - Alerts are sent to a unique set of recipients from both the Owners and Issued To fields.
  - The email body includes an HTML table listing the certificates that meet the expiration criteria, along with required details.

# The Current Status

Emails are sent by grouping recipients by certificate owner and expiration timeline. Gmail SMTP is used to send alerts, with customised HTML email templates. The database currently contains sample data for testing purposes. While unit tests are not yet implemented, the script includes if conditions to outline the core logic and requirements.

# ⚠️ The Limitations

- No Unit Tests → increases risk of unnoticed failures.
- Excessive Expired Alerts → currently, daily emails are sent for already expired certificates, causing notification fatigue.
- Data Validation Gaps → no constraints to enforce correct certificate data formats, leaving potential security risks.
- Lack of Real-Time Automation → the system cannot yet automatically fetch certificate details from the host system.

# 📌 The Next Steps

- Modify alert rules → stop daily expired alerts; only send on 7, 14, or 30 days post-expiration.
- Add database constraints → ensure only valid and secure certificate data can be stored.
- Explore solutions to automatically retrieve local certificate data and insert it into the database.
- Implement unit tests to maintain clean commits and reliable pull requests.

# 🚀 The Future Vision

The long-term goal is to integrate these incremental services into a unified certificate management platform that can: Automatically renew, replace, or remove certificates, enforce organisational policies and approval workflows, ensure full compliance and operational security. While the journey is ongoing, each small step brings us closer to a robust, enterprise-grade certificate orchestration solution. Contributions are always welcome!

If there's any queries, then please feel free to mention them in the discussion channel.
