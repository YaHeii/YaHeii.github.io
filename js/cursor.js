// themes/stellar/source/js/particle-cursor.js

document.addEventListener('DOMContentLoaded', () => {
    const PARTICLES_NUMBER = 20; // 同时存在的粒子数量
    const PARTICLE_SIZE = 4;     // 粒子基础大小 (px)
    const PARTICLE_SPEED = 0.5;  // 粒子运动速度
    const PARTICLE_FADE = 0.01;  // 粒子淡出速度

    let particles = [];
    let cursor = { x: window.innerWidth / 2, y: window.innerHeight / 2 };

    // 监听鼠标移动
    document.addEventListener('mousemove', (e) => {
        cursor.x = e.clientX;
        cursor.y = e.clientY;
    });

    function createParticle(x, y) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        document.body.appendChild(particle);

        const size = Math.random() * PARTICLE_SIZE + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;

        const angle = Math.random() * 2 * Math.PI;
        const speed = Math.random() * PARTICLE_SPEED;

        return {
            element: particle,
            x: x,
            y: y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            alpha: 1
        };
    }

    function animateParticles() {
        // 如果粒子池未满，且有一定概率，则在鼠标位置创建新粒子
        if (particles.length < PARTICLES_NUMBER && Math.random() > 0.5) {
             particles.push(createParticle(cursor.x, cursor.y));
        }

        particles.forEach((p, index) => {
            // 更新位置和透明度
            p.x += p.vx;
            p.y += p.vy;
            p.alpha -= PARTICLE_FADE;

            // 如果粒子完全淡出，则从 DOM 和数组中移除
            if (p.alpha <= 0) {
                p.element.remove();
                particles.splice(index, 1);
            } else {
                // 应用变换
                p.element.style.transform = `translate3d(${p.x}px, ${p.y}px, 0px)`;
                p.element.style.opacity = p.alpha;
            }
        });

        requestAnimationFrame(animateParticles);
    }
    
    // 隐藏默认光标
    document.body.style.cursor = 'none';

    animateParticles();
});