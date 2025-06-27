const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const mineflayer = require("mineflayer");

const skills = require("./lib/skillLoader");
const { initCounter, getNextTime } = require("./lib/utils");
const obs = require("./lib/observation/base");
const OnChat = require("./lib/observation/onChat");
const OnError = require("./lib/observation/onError");
const { Voxels, BlockRecords } = require("./lib/observation/voxels");
const Status = require("./lib/observation/status");
const Inventory = require("./lib/observation/inventory");
const OnSave = require("./lib/observation/onSave");
const Chests = require("./lib/observation/chests");
const { plugin: tool } = require("mineflayer-tool");
const { mineflayer: mineflayerViewer } = require("prismarine-viewer");

let bot = null;

const app = express();

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

app.post("/start", (req, res) => {
    const v8 = require('v8');

    const heapLimitMB = v8.getHeapStatistics().heap_size_limit / 1024 / 1024;
    console.log(`🧠 Heap memory limit: ${Math.round(heapLimitMB)} MB`);

    const used = process.memoryUsage().heapUsed / 1024 / 1024;
    console.log(`💾 Heap used: ${Math.round(used * 100) / 100} MB`);
    if (bot) onDisconnect("Restarting bot");
    bot = null;
    bot = mineflayer.createBot({
        host: "localhost", // minecraft server ip
        port: req.body.port, // minecraft server port
        username: "bot",
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    });
    bot.once("error", onConnectionFailed);

    // Event subscriptions
    bot.waitTicks = req.body.waitTicks;
    bot.globalTickCounter = 0;
    bot.stuckTickCounter = 0;
    bot.stuckPosList = [];
    bot.iron_pickaxe = false;

    bot.on("kicked", onDisconnect);

    // mounting will cause physicsTick to stop
    bot.on("mount", () => {
        bot.dismount();
    });

    bot.on("error", (err) => {
        console.error("Bot error:", err);
    });

    bot.once("spawn", async () => {
        bot.removeListener("error", onConnectionFailed);
        console.log("✅ Bot spawned");

        //use the link to view the bot's view: http://localhost:3001/
        mineflayerViewer(bot, { port: 3001, firstPerson: false });
        await bot.waitForTicks(10);

        let itemTicks = 1;
        if (req.body.reset === "hard") {
            bot.chat("/clear @s");
            bot.chat("/kill @s");
            const inventory = req.body.inventory ? req.body.inventory : {};
            const equipment = req.body.equipment
                ? req.body.equipment
                : [null, null, null, null, null, null];
            for (let key in inventory) {
                bot.chat(`/give @s minecraft:${key} ${inventory[key]}`);
                itemTicks += 1;
            }
            const equipmentNames = [
                "armor.head",
                "armor.chest",
                "armor.legs",
                "armor.feet",
                "weapon.mainhand",
                "weapon.offhand",
            ];
            for (let i = 0; i < 6; i++) {
                if (i === 4) continue;
                if (equipment[i]) {
                    bot.chat(
                        `/item replace entity @s ${equipmentNames[i]} with minecraft:${equipment[i]}`
                    );
                    itemTicks += 1;
                }
            }
        }

        if (req.body.position) {
            bot.chat(
                `/tp @s ${req.body.position.x} ${req.body.position.y} ${req.body.position.z}`
            );
        }

        // if iron_pickaxe is in bot's inventory
        if (
            bot.inventory.items().find((item) => item.name === "iron_pickaxe")
        ) {
            bot.iron_pickaxe = true;
        }

        const { pathfinder } = require("mineflayer-pathfinder");
        const tool = require("mineflayer-tool").plugin;
        const collectBlock = require("mineflayer-collectblock").plugin;
        const pvp = require("mineflayer-pvp").plugin;
        bot.loadPlugin(pathfinder);
        bot.loadPlugin(tool);
        bot.loadPlugin(collectBlock);
        bot.loadPlugin(pvp);

        // bot.collectBlock.movements.digCost = 0;
        // bot.collectBlock.movements.placeCost = 0;

        obs.inject(bot, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
        ]);
        skills.inject(bot);

        if (req.body.spread) {
            bot.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot.waitForTicks(bot.waitTicks);
        }

        await bot.waitForTicks(bot.waitTicks * itemTicks);
        let observation = null;
        try {
            observation = bot.observe();  // crash risk here
            console.log("📦 Observation ready, sending to client.");
            res.json(observation);
        } catch (err) {
            console.error("❌ Observation error:", err);
            res.status(500).json({ error: "Failed to observe" });
        }

        initCounter(bot);
        bot.chat("/gamerule keepInventory true");
        bot.chat("/gamerule doDaylightCycle false");

    });

    function onConnectionFailed(e) {
        console.log(e);
        bot = null;
        res.status(400).json({ error: e });
    }
    function onDisconnect(message) {
        if (bot.viewer) {
            bot.viewer.close();
        }
        bot.removeAllListeners();
        bot.end();
        console.log(message);
        bot = null;
    }
});

app.post("/step", async (req, res) => {
    // import useful package
    let response_sent = false;
    function otherError(err) {
        console.log("Uncaught Error");
        bot.emit("error", handleError(err));
        bot.waitForTicks(bot.waitTicks).then(() => {
            if (!response_sent) {
                response_sent = true;
                res.json(bot.observe());
            }
        });
    }

    const mcData = require("minecraft-data")(bot.version);
    mcData.itemsByName["leather_cap"] = mcData.itemsByName["leather_helmet"];
    mcData.itemsByName["leather_tunic"] =
        mcData.itemsByName["leather_chestplate"];
    mcData.itemsByName["leather_pants"] =
        mcData.itemsByName["leather_leggings"];
    mcData.itemsByName["leather_boots"] = mcData.itemsByName["leather_boots"];
    mcData.itemsByName["lapis_lazuli_ore"] = mcData.itemsByName["lapis_ore"];
    mcData.blocksByName["lapis_lazuli_ore"] = mcData.blocksByName["lapis_ore"];
    const {
        Movements,
        goals: {
            Goal,
            GoalBlock,
            GoalNear,
            GoalXZ,
            GoalNearXZ,
            GoalY,
            GoalGetToBlock,
            GoalLookAtBlock,
            GoalBreakBlock,
            GoalCompositeAny,
            GoalCompositeAll,
            GoalInvert,
            GoalFollow,
            GoalPlaceBlock,
        },
        pathfinder,
        Move,
        ComputedPath,
        PartiallyComputedPath,
        XZCoordinates,
        XYZCoordinates,
        SafeBlock,
        GoalPlaceBlockOptions,
    } = require("mineflayer-pathfinder");
    const { Vec3 } = require("vec3");

    // Set up pathfinder
    const movements = new Movements(bot, mcData);
    bot.pathfinder.setMovements(movements);

    bot.globalTickCounter = 0;
    bot.stuckTickCounter = 0;
    bot.stuckPosList = [];

    function onTick() {
        bot.globalTickCounter++;
        if (bot.pathfinder.isMoving()) {
            bot.stuckTickCounter++;
            if (bot.stuckTickCounter >= 100) {
                onStuck(1.5);
                bot.stuckTickCounter = 0;
            }
        }
    }

    bot.on("physicsTick", onTick);

    // initialize fail count
    let _craftItemFailCount = 0;
    let _killMobFailCount = 0;
    let _mineBlockFailCount = 0;
    let _placeItemFailCount = 0;
    let _smeltItemFailCount = 0;

    // Retrieve array form post bod
    const code = req.body.code;
    const programs = req.body.programs;
    bot.cumulativeObs = [];
    await bot.waitForTicks(bot.waitTicks);

    let timeoutReached = false;
    const TIMEOUT_MS = 10 * 60 * 1000; // 10 minutes
    
    // Start the timer
    const timeout = setTimeout(() => {
        timeoutReached = true;
        console.warn("Timeout reached: Code execution exceeded 5 minutes.");
        if (!response_sent) {
            response_sent = true;
            res.status(200).json([
                ["onError", { onError: "TimeoutError: Code execution exceeded 5 minutes." }],
                ...bot.cumulativeObs,
                ...bot.observe()
            ]);            
        }
    }, TIMEOUT_MS);
    
    // Run the code
    console.log("⏳ Code execution starting...");
    console.log(`💾 Heap before: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`);
    const r = await evaluateCode(code, programs);
    console.log(`✅ Code execution finished.`);
    console.log(`💾 Heap after: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`);
    
    // Cancel timer if finished on time
    clearTimeout(timeout);
    process.off("uncaughtException", otherError);
    
    // Emit error if code failed, but not due to timeout
    if (!timeoutReached && r !== "success") {
        const errMsg = handleError(r);
        bot.cumulativeObs.push([
            "onError",
            Object.assign({ onError: errMsg }, bot.observe?.() || {})
        ]);
    }

    await returnItems();
    // wait for last message
    await bot.waitForTicks(bot.waitTicks);
    if (!response_sent) {
        response_sent = true;
        try {
            if (bot) {
                res.status(200).json([
                    ...bot.cumulativeObs,
                    ...bot.observe()
                ]);                
            } else {
                res.status(200).json([
                    ["onError", { onError: "Bot not found" }],
                    ...bot.cumulativeObs,
                    ...bot.observe()
                ]);
            }
        } catch (e) {
            res.status(200).json([
                ["onError", { onError: "Failed to observe after timeout" }],
                ...bot.cumulativeObs,
                ...bot.observe()
            ]);
        }
    }    
    bot.removeListener("physicsTick", onTick);

    async function evaluateCode(code, programs) {
        try {
            const wrappedCode = `(async () => {
                try {
                    ${programs}
                    ${code}
                } catch (innerError) {
                    throw new Error("Runtime error: " + innerError.message);
                }
            })()`;
    
            await eval(wrappedCode);
            return "success";
        } catch (err) {
            return new Error("Evaluation error: " + (err?.message || String(err)));
        }
    }

    function onStuck(posThreshold) {
        const currentPos = bot.entity.position;
        bot.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot.stuckPosList.length === 5) {
            const oldestPos = bot.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot(); // execute the function
            }

            // Remove the oldest time from the list
            bot.stuckPosList.shift();
        }
    }

    function teleportBot() {
        const blocks = bot.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot.chat("/tp @s ~ ~1.25 ~");
        }
    }

    function returnItems() {
        bot.chat("/gamerule doTileDrops false");
        const crafting_table = bot.findBlock({
            matching: mcData.blocksByName.crafting_table.id,
            maxDistance: 128,
        });
        if (crafting_table) {
            bot.chat(
                `/setblock ${crafting_table.position.x} ${crafting_table.position.y} ${crafting_table.position.z} air destroy`
            );
            bot.chat("/give @s crafting_table");
        }
        const furnace = bot.findBlock({
            matching: mcData.blocksByName.furnace.id,
            maxDistance: 128,
        });
        if (furnace) {
            bot.chat(
                `/setblock ${furnace.position.x} ${furnace.position.y} ${furnace.position.z} air destroy`
            );
            bot.chat("/give @s furnace");
        }
        if (bot.inventoryUsed() >= 32) {
            // if chest is not in bot's inventory
            if (!bot.inventory.items().find((item) => item.name === "chest")) {
                bot.chat("/give @s chest");
            }
        }
        // if iron_pickaxe not in bot's inventory and bot.iron_pickaxe
        if (
            bot.iron_pickaxe &&
            !bot.inventory.items().find((item) => item.name === "iron_pickaxe")
        ) {
            bot.chat("/give @s iron_pickaxe");
        }
        bot.chat("/gamerule doTileDrops true");
    }

    function handleError(err) {
        const stack = err.stack;
        if (!stack) return err;
    
        console.log(stack);
        const lines = stack.split("\n");
        const final_line = lines[1] || "";
    
        const regex = /<anonymous>:(\d+):\d+\)/;
        const programs_length = Array.isArray(programs) ? programs.length : 0;
    
        let match_line = null;
        for (const line of lines) {
            const match = regex.exec(line);
            if (match) {
                const line_num = parseInt(match[1], 10);
                if (!isNaN(line_num) && line_num >= programs_length) {
                    match_line = line_num - programs_length;
                    break;
                }
            }
        }
    
        if (!match_line) return err.message;
    
        const f_line = final_line.match(/\((?<file>.*):(?<line>\d+):(?<pos>\d+)\)/);
    
        if (f_line?.groups?.file && fs.existsSync(f_line.groups.file)) {
            const { file, line } = f_line.groups;
            const fileLines = fs.readFileSync(file, "utf8").split("\n");
            const fileSourceLine = fileLines[line - 1] || "";
            const codeLine = code.split("\n")[match_line - 1] || "";
    
            return `${file}:${line}\n${fileSourceLine.trim()}\n${err.message}\nat ${codeLine.trim()} in your code`;
        }
    
        if (f_line?.groups?.file?.includes("<anonymous>")) {
            const { line } = f_line.groups;
            const matchLine = Number(match_line);
            const codeLine = code.split("\n")[matchLine - 1] || "";
            const progLine = programs.split("\n")[line - 1] || "";
    
            if (line < programs_length) {
                return `In your program code:\n${progLine.trim()}\n${err.message}`;
            }
    
            return `Your code:${matchLine}\n${codeLine.trim()}\n${err.message}`;
        }
    
        return err.message;
    }
});

app.post("/stop", (req, res) => {
    bot.end();
    res.json({
        message: "Bot stopped",
    });
});

app.post("/pause", (req, res) => {
    if (!bot) {
        res.status(400).json({ error: "Bot not spawned" });
        return;
    }
    bot.chat("/pause");
    bot.waitForTicks(bot.waitTicks).then(() => {
        res.json({ message: "Success" });
    });
});

// Server listening to PORT 3000
const DEFAULT_PORT = 3000;
const PORT = process.argv[2] || DEFAULT_PORT;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});
