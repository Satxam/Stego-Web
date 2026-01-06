 Stego-Web | Digital Forensics Tool



[Click Here to View Live Project](https://satyam-stego-web.onrender.com/)

---

## 📖 What is this?
**Stego-Web** is a cybersecurity tool that lets you hide secret text messages inside images. To the naked eye, the image looks exactly the same, but it contains hidden data that can only be revealed using this tool.


---


This tool supports two different hiding methods depending on the image type:

### 1. PNG Images (Pixel Hiding)
LSB (Least Significant Bit).
The tool modifies the invisible bits of the image pixels.


### 2. JPG/JPEG Images (Metadata Hiding)
 Exif Data Manipulation.
The tool hides the message inside the file headers (where camera info is usually stored).


---

 Tech Stack
* Frontend:** HTML5, CSS3 (Custom Responsive Design)
* Backend:** Python (Flask Framework)
* Libraries:** `stegano`, `Pillow`, `werkzeug`
* Deployment: Render (Cloud Hosting)

---


If you want to run this project on your own computer, follow these steps:

1. Clone the Repository
```bash
git clone [https://github.com/Satxam/stego-web.git](https://github.com/Satxam/stego-web.git)
cd stego-web