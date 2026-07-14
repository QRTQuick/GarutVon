/* GarutVON v2 - 3D Interactive Visual Engine (Canvas Particles & Parallax Depth) */

document.addEventListener("DOMContentLoaded", () => {
    initParticles();
    initHoverDepth();
});

// 1. High Performance Canvas-Based Particle System with Mouse Interactions
function initParticles() {
    const canvas = document.getElementById("particle-canvas");
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d");
    let particles = [];
    let mouse = { x: null, y: null, radius: 120 };
    
    // Resize handler
    function resizeCanvas() {
        canvas.width = canvas.parentElement.offsetWidth;
        canvas.height = canvas.parentElement.offsetHeight;
        spawnParticles();
    }
    
    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 1.5 + 0.5;
            this.baseX = this.x;
            this.baseY = this.y;
            this.density = (Math.random() * 30) + 15;
            this.color = "rgba(255, 255, 255, " + (Math.random() * 0.3 + 0.1) + ")";
        }
        
        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.closePath();
            ctx.fill();
        }
        
        update() {
            // Check mouse proximity
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            let forceDirectionX = dx / distance;
            let forceDirectionY = dy / distance;
            
            // Max force
            let maxDistance = mouse.radius;
            let force = (maxDistance - distance) / maxDistance;
            
            if (distance < mouse.radius) {
                let directionX = forceDirectionX * force * this.density;
                let directionY = forceDirectionY * force * this.density;
                this.x -= directionX;
                this.y -= directionY;
            } else {
                // Return to original anchor coordinates
                if (this.x !== this.baseX) {
                    let dxBase = this.x - this.baseX;
                    this.x -= dxBase / 10;
                }
                if (this.y !== this.baseY) {
                    let dyBase = this.y - this.baseY;
                    this.y -= dyBase / 10;
                }
            }
        }
    }
    
    function spawnParticles() {
        particles = [];
        // Spawn based on screen density
        const quantity = Math.floor((canvas.width * canvas.height) / 14000);
        for (let i = 0; i < quantity; i++) {
            let x = Math.random() * canvas.width;
            let y = Math.random() * canvas.height;
            particles.push(new Particle(x, y));
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }
        requestAnimationFrame(animate);
    }
    
    // Attach event listeners
    window.addEventListener("resize", resizeCanvas);
    
    canvas.parentElement.addEventListener("mousemove", (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });
    
    canvas.parentElement.addEventListener("mouseleave", () => {
        mouse.x = null;
        mouse.y = null;
    });
    
    // Start Canvas Run
    resizeCanvas();
    animate();
}

// 2. Interactive Parallax Hover Depth Effect (Tilt Card mechanics)
function initHoverDepth() {
    const cards = document.querySelectorAll(".hover-depth-card");
    
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position inside element
            const y = e.clientY - rect.top;  // y position inside element
            
            // Calculate relative coordinate factors from center
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const deltaX = (x - centerX) / centerX; // ranges from -1 to 1
            const deltaY = (y - centerY) / centerY; // ranges from -1 to 1
            
            // Max tilt of 10 degrees
            const tiltX = (deltaY * 10).toFixed(2);
            const tiltY = -(deltaX * 10).toFixed(2);
            
            card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
            card.style.boxShadow = `${-tiltY * 2}px ${tiltX * 2}px 30px rgba(255, 255, 255, 0.08)`;
        });
        
        card.addEventListener("mouseleave", () => {
            // Restore smooth equilibrium
            card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
            card.style.boxShadow = "none";
        });
    });
}
