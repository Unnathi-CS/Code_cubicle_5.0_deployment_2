// Starfield Animation with Three.js
// Creates a beautiful animated starfield background

class StarfieldAnimation {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id "${containerId}" not found`);
            return;
        }

        this.init();
    }

    init() {
        // Set up scene, camera, and renderer
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, this.container.offsetWidth / this.container.offsetHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ alpha: true });
        this.renderer.setSize(this.container.offsetWidth, this.container.offsetHeight);
        this.renderer.setClearColor(0x000000, 0); // Transparent background
        this.container.appendChild(this.renderer.domElement);

        // Starfield parameters
        this.starCount = 700;
        this.starField = {
            minZ: -200,
            maxZ: -1000,
            width: 1000,
            height: 1000,
            speed: 1.1
        };

        this.createStars();
        this.createShootingStars();
        this.setupEventListeners();
        this.animate();
    }

    createStars() {
        // Create stars
        const starsGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(this.starCount * 3);
        const opacities = new Float32Array(this.starCount);

        // Function to generate a random position within our desired range
        const generateStarPosition = () => {
            return {
                x: (Math.random() - 0.5) * this.starField.width,
                y: (Math.random() - 0.5) * this.starField.height,
                z: Math.random() * (this.starField.maxZ - this.starField.minZ) + this.starField.minZ
            };
        };

        // Initialize star positions and opacities
        for (let i = 0; i < this.starCount; i++) {
            const pos = generateStarPosition();
            positions[i * 3] = pos.x;
            positions[i * 3 + 1] = pos.y;
            positions[i * 3 + 2] = pos.z;
            opacities[i] = Math.random();
        }

        starsGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        starsGeometry.setAttribute("opacity", new THREE.BufferAttribute(opacities, 1));

        // Create star material with custom shader for individual star opacity
        const starsMaterial = new THREE.ShaderMaterial({
            transparent: true,
            uniforms: {
                size: { value: 2.0 },
                color: { value: new THREE.Color(0xFFFFFF) },
            },
            vertexShader: `
                attribute float opacity;
                varying float vOpacity;
                void main() {
                    vOpacity = opacity;
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    gl_PointSize = 2.0 * (300.0 / -mvPosition.z);
                }
            `,
            fragmentShader: `
                varying float vOpacity;
                uniform vec3 color;
                void main() {
                    float r = length(gl_PointCoord - vec2(0.5));
                    if (r > 0.5) discard;
                    gl_FragColor = vec4(color, vOpacity);
                }
            `
        });

        this.stars = new THREE.Points(starsGeometry, starsMaterial);
        this.scene.add(this.stars);
    }

    createShootingStars() {
        // Shooting star setup
        class ShootingStar {
            constructor(scene) {
                this.scene = scene;
                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(2 * 3);
                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                
                const material = new THREE.LineBasicMaterial({
                    color: 0xFFFFFF,
                    transparent: true,
                    opacity: 1
                });

                this.line = new THREE.Line(geometry, material);
                this.reset();
                this.scene.add(this.line);
            }

            reset() {
                const start = this.generateStarPosition();
                const angle = Math.random() * Math.PI * 2;
                const length = 50 + Math.random() * 100;
                
                const positions = this.line.geometry.attributes.position.array;
                positions[0] = start.x;
                positions[1] = start.y;
                positions[2] = start.z;
                positions[3] = start.x + Math.cos(angle) * length;
                positions[4] = start.y + Math.sin(angle) * length;
                positions[5] = start.z;
                
                this.line.geometry.attributes.position.needsUpdate = true;
                this.life = 1.0;
                this.speed = 0.02 + Math.random() * 0.03;
            }

            generateStarPosition() {
                return {
                    x: (Math.random() - 0.5) * 1000,
                    y: (Math.random() - 0.5) * 1000,
                    z: Math.random() * (-1000 - (-200)) + (-200)
                };
            }

            update() {
                this.life -= this.speed;
                this.line.material.opacity = this.life;
                
                if (this.life <= 0) {
                    this.reset();
                    return false;
                }
                return true;
            }
        }

        // Create shooting stars
        this.shootingStars = Array(3).fill(null).map(() => new ShootingStar(this.scene));
    }

    setupEventListeners() {
        // Handle window resizing
        window.addEventListener("resize", () => {
            const width = this.container.offsetWidth;
            const height = this.container.offsetHeight;
            
            this.renderer.setSize(width, height);
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
        });
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Update star positions and twinkle effect
        const positions = this.stars.geometry.attributes.position.array;
        const opacities = this.stars.geometry.attributes.opacity.array;
        
        for (let i = 0; i < this.starCount; i++) {
            // Update positions
            positions[i * 3 + 2] += this.starField.speed;

            // Reset stars that pass the camera
            if (positions[i * 3 + 2] > this.starField.minZ) {
                const pos = {
                    x: (Math.random() - 0.5) * this.starField.width,
                    y: (Math.random() - 0.5) * this.starField.height,
                    z: this.starField.maxZ
                };
                positions[i * 3] = pos.x;
                positions[i * 3 + 1] = pos.y;
                positions[i * 3 + 2] = pos.z;
            }

            // Twinkle effect
            opacities[i] += (Math.random() - 0.5) * 0.1;
            opacities[i] = Math.max(0.2, Math.min(1, opacities[i]));
        }

        // Update shooting stars
        this.shootingStars.forEach(shootingStar => shootingStar.update());

        // Subtle camera movement
        this.camera.position.x += (Math.random() - 0.5) * 0.2;
        this.camera.position.y += (Math.random() - 0.5) * 0.2;

        // Update the geometry
        this.stars.geometry.attributes.position.needsUpdate = true;
        this.stars.geometry.attributes.opacity.needsUpdate = true;

        // Render the scene
        this.renderer.render(this.scene, this.camera);
    }

    destroy() {
        if (this.renderer) {
            this.renderer.dispose();
            if (this.container && this.renderer.domElement) {
                this.container.removeChild(this.renderer.domElement);
            }
        }
    }
}

// Initialize starfield when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if Three.js is loaded
    if (typeof THREE === 'undefined') {
        console.error('Three.js is not loaded. Please include Three.js before this script.');
        return;
    }
    
    // Initialize starfield animation
    window.starfieldAnimation = new StarfieldAnimation('space-animation');
});
