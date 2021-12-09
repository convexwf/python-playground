# Python Playground

This is a collection of Python scripts that I have written to learn Python.

## TIMRecordBackup

TIM is a popular instant messaging app which is known as the lite version of QQ in China.

The TIM Chat Record Exporter is a tool designed to backup and export chat records from the TIM messaging application. This project allows users to specify which friends and groups to export, supporting the export of both images and text. The exported content is then written into a markdown file for easy access and readability.

The motivation behind developing this project stems from the limitations of TIM itself. TIM does not natively support the export of chat records, and its search functionality is limited for longer periods. Moreover, chat records are at risk of being lost when a user clears their phone. TIM stores chat records in a SQLite database, and by understanding the database structure and using a key file for database authentication, users can retrieve all chat records within a specified time range.

By utilizing this tool, users can take control of their chat history, ensuring that important conversations are safely backed up and accessible whenever needed. The TIM Chat Record Exporter provides a convenient solution for users who value their chat history and want to preserve it for future reference.
