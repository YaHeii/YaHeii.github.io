// 立即执行函数，避免污染全局作用域
(function() {
    // 如果是移动设备，则不执行效果
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        return;
    }

    // 创建 canvas 元素
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // 设置 canvas 样式，使其作为背景
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '-1'; // 关键：将 canvas 置于最底层
    canvas.style.pointerEvents = 'none'; // 关键：让鼠标事件可以穿透 canvas

    // 将 canvas 添加到 body
    document.body.appendChild(canvas);

    let mouse = { x: null, y: null };
    let particles = [];
    
    // ---- 可自定义的参数 ----
    const particleCount = 25; // 粒子数量
    const particleSpeed = 2;   // 粒子移动速度
    const particleSize = 3;    // 粒子大小
    const particleColor = 'rgba(180, 180, 180, 0.5)'; // 粒子颜色
    const connectionDistance = 150; // 粒子之间连线的最大距离
    // ----------------------

    function updateCanvasSize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);

    document.addEventListener('mousemove', function(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    class Particle {
        constructor() {
            this.x = mouse.x || Math.random() * canvas.width;
            this.y = mouse.y || Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * particleSpeed;
            this.vy = (Math.random() - 0.5) * particleSpeed;
            this.size = Math.random() * particleSize + 1;
        }

        update() {
            // 边界检测
            if (this.x > canvas.width || this.x < 0) this.vx = -this.vx;
            if (this.y > canvas.height || this.y < 0) this.vy = -this.vy;

            this.x += this.vx;
            this.y += this.vy;
        }

        draw() {
            ctx.beginPath();
            ctx.fillStyle = particleColor;
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function init() {
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function handleParticles() {
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            // 粒子之间的连线
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < connectionDistance) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(180, 180, 180, ${1 - distance / connectionDistance})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }

            // 粒子与鼠标的连线
            if (mouse.x) {
                const mdx = particles[i].x - mouse.x;
                const mdy = particles[i].y - mouse.y;
                const mouseDistance = Math.sqrt(mdx * mdx + mdy * mdy);
                if (mouseDistance < connectionDistance) {
                     ctx.beginPath();
                     ctx.strokeStyle = `rgba(180, 180, 180, ${1 - mouseDistance / connectionDistance})`;
                     ctx.lineWidth = 0.5;
                     ctx.moveTo(particles[i].x, particles[i].y);
                     ctx.lineTo(mouse.x, mouse.y);
                     ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        handleParticles();
        requestAnimationFrame(animate);
    }
    
    init();
    animate();

})();