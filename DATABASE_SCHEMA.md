# URL.ly Database Schema

This document provides a comprehensive overview of the database models and their relationships in the URL.ly project.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     URL.LY DATABASE                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐          1:1           ┌─────────────────────┐
│     CustomUser      │◄─────────────────────► │    UserProfile      │
├─────────────────────┤                        ├─────────────────────┤
│ PK  id (UUID)       │                        │ PK  id (UUID)       │
│     email (unique)  │                        │ FK  user ──────────►│
│     username        │                        │     first_name      │
│     password        │                        │     last_name       │
│     is_active       │                        │     phone_number    │
│     is_staff        │                        │     profile_image   │
│     created_at      │                        │     gender          │
│     updated_at      │                        │     created_at      │
└─────────┬───────────┘                        │     updated_at      │
          │                                    └─────────────────────┘
          │
          │ 1:1
          ▼
┌─────────────────────┐           1:N          ┌─────────────────────┐
│  BioLinkProfile     │◄─────────────────────► │        Link         │
├─────────────────────┤                        ├─────────────────────┤
│ PK  id (UUID)       │                        │ PK  id (UUID)       │
│ FK  user ───────────┤                        │ FK  profile ───────►│
│     display_name    │                        │     title           │
│     bio             │                        │     url             │
│     profile_image   │                        │     is_public       │
│     public_slug     │                        │     created_at      │
└─────────────────────┘                        └─────────────────────┘

          │
          │ 1:N (CustomUser)
          ▼
┌─────────────────────┐           1:N          ┌─────────────────────┐
│      UrlModel       │◄─────────────────────► │      UrlVisit       │
├─────────────────────┤                        ├─────────────────────┤
│ PK  id (auto)       │                        │ PK  id (auto)       │
│     original_url    │                        │ FK  url ───────────►│
│     short_url       │                        │     timestamp       │
│     qrcode          │                        │     ip_address      │
│     created_at      │                        │     country         │
│     expires_at      │                        │     region          │
│     click_count     │                        │     city            │
│ FK  user ───────────┤                        │     browser         │
└─────────────────────┘                        │     os              │
                                               │     device          │
                                               │     referrer        │
                                               │     is_bot          │
                                               └─────────────────────┘


┌─────────────────────┐                        ┌─────────────────────┐
│ ShortUrlAnonymous   │                        │      Contact        │
├─────────────────────┤                        ├─────────────────────┤
│ PK  id (auto)       │      (standalone)      │ PK  id (UUID)       │
│     original_url    │                        │     name            │
│     short_code      │                        │     email           │
│     ip_address      │                        │     message         │
│     created_at      │                        │     created_at      │
└─────────────────────┘                        └─────────────────────┘
```

---

## Relationships Summary

| Relationship | From | To | Type | Description |
|--------------|------|-----|------|-------------|
| `user_profile_link` | `CustomUser` | `UserProfile` | **1:1** | Each user has one profile |
| `biolinkprofile` | `CustomUser` | `BioLinkProfile` | **1:1** | Each user has one biolink page |
| `links` | `BioLinkProfile` | `Link` | **1:N** | Profile can have many links |
| `user` | `CustomUser` | `UrlModel` | **1:N** | User can create many short URLs |
| `visits` | `UrlModel` | `UrlVisit` | **1:N** | Each URL tracks many visits |

---

## Models by App

### Auth App

#### CustomUser
Extended Django user model with email-based authentication.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `email` | EmailField | Unique, used for login |
| `username` | CharField | Display username |
| `password` | CharField | Hashed password |
| `is_active` | BooleanField | Email verified status |
| `is_staff` | BooleanField | Admin access |
| `created_at` | DateTimeField | Account creation timestamp |
| `updated_at` | DateTimeField | Last update timestamp |

#### UserProfile
Additional user information and preferences.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user` | OneToOneField | Link to CustomUser |
| `first_name` | CharField | User's first name |
| `last_name` | CharField | User's last name |
| `phone_number` | PhoneNumberField | Contact number |
| `profile_image` | ImageField | Avatar (max 2MB) |
| `gender` | CharField | M/F/Other |
| `created_at` | DateTimeField | Profile creation timestamp |
| `updated_at` | DateTimeField | Last update timestamp |

#### Contact
Contact form submissions storage.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField | Sender's name |
| `email` | EmailField | Sender's email |
| `message` | TextField | Message content (max 300 chars) |
| `created_at` | DateTimeField | Submission timestamp |

---

### Biolink App

#### BioLinkProfile
User's customizable link-in-bio page.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user` | OneToOneField | Link to CustomUser |
| `display_name` | CharField | Public display name |
| `bio` | CharField | Short bio (max 200 chars) |
| `profile_image` | ImageField | Profile picture (auto-optimized) |
| `public_slug` | SlugField | Custom URL slug |

#### Link
Individual links within a biolink profile.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `profile` | ForeignKey | Link to BioLinkProfile |
| `title` | CharField | Link display text |
| `url` | URLField | Destination URL |
| `is_public` | BooleanField | Visibility toggle |
| `created_at` | DateTimeField | Creation timestamp |

---

### urlLogic App

#### UrlModel
Shortened URLs for authenticated users.

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `original_url` | URLField | Original long URL |
| `short_url` | CharField | Generated short code |
| `qrcode` | ImageField | QR code image |
| `created_at` | DateTimeField | Creation timestamp |
| `expires_at` | DateTimeField | Expiration date (optional) |
| `click_count` | PositiveIntegerField | Total clicks |
| `user` | ForeignKey | Link to CustomUser |

#### UrlVisit
Analytics tracking for each URL visit.

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `url` | ForeignKey | Link to UrlModel |
| `timestamp` | DateTimeField | Visit timestamp |
| `ip_address` | GenericIPAddressField | Visitor IP |
| `country` | CharField | Geo: Country |
| `region` | CharField | Geo: Region/State |
| `city` | CharField | Geo: City |
| `browser` | CharField | Browser name |
| `os` | CharField | Operating system |
| `device` | CharField | Device type |
| `referrer` | URLField | Referring URL |
| `is_bot` | BooleanField | Bot detection flag |

#### ShortUrlAnonymous
Shortened URLs for non-authenticated users.

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `original_url` | URLField | Original long URL |
| `short_code` | CharField | Generated short code |
| `ip_address` | GenericIPAddressField | Creator's IP |
| `created_at` | DateTimeField | Creation timestamp |

---

## Security Features

- **UUID Primary Keys**: Used across most models for enhanced security
- **Email Verification**: Users must verify email before `is_active` is set
- **File Size Validation**: Profile images limited to 2MB
- **URL Blacklisting**: Prevents self-referential shortened URLs
- **Image Optimization**: Automatic resizing and compression for uploads

---

## Notes

- All timestamps use `auto_now_add` for creation and `auto_now` for updates
- Media files are stored in Cloudinary (production) or local `media/` folder (development)
- The `Brandlink` app is currently under development (models commented out)

---

*Last updated: December 2024*
